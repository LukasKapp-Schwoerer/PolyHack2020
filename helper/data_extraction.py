import pandas as pd
import math

class Congestion:
    def __init__(self, passenger_value=0, freight_value=0):
        self.passenger_value = passenger_value
        self.freight_value = freight_value

    def __str__(self):
        return f"passenger_value: {self.passenger_value} | freight_value: {self.freight_value}"

    def __add__(self, other):
        return Congestion(self.passenger_value + other.passenger_value, self.freight_value + other.passenger_value)

    def increase_passenger_value(self, increment):
        self.passenger_value += increment

    def increase_freight_value(self, increment):
        self.freight_value += increment

class Operating_point:
    def __init__(self, id_index, id_word, gps):
        self.id_index = id_index
        self.id_word = id_word
        self.gps = gps
        self.connections_inbound = []
        self.connections_outbound = []
        self.congestion = Congestion()
        self.lines = []

    def add_connection_outbound(self, connection):
        self.connections_outbound.append(connection)

    def add_connection_inbound(self, connection):
        self.connections_inbound.append(connection)

    def add_line(self, line_id):
        self.lines.append(line_id)

    def __str__(self):
        return f"{self.id_index:d} {self.id_word} {self.gps} " +                f"outbound: {self.connections_outbound} | inbound: {self.connections_inbound}\n"                f"congestion: {self.congestion}"

class Connection:
    def __init__(self, from_op, to_op, trains, load, train_type):
        self.from_op = from_op
        self.to_op = to_op
        self.trains = trains
        self.load = load
        self.train_type = train_type

    def __str__(self):
        return f"{self.from_op} {self.to_op} {self.trains} {self.load}"

class Connection_congestion:
    def __init__(self, smaller_op, greater_op, congestion=None):
        self.smaller_op = smaller_op
        self.greater_op = greater_op
        if congestion is not None:
            self.congestion = congestion
        else:
            self.congestion = Congestion()


    def __str__(self):
        return f"Connection_congestion {self.smaller_op} <-> {self.greater_op}: " + str(self.congestion) + "\n"


class Data_extractor:
    def __init__(self, data_dir):
        self.points = dict()

        self.operating_points_df = pd.read_csv(data_dir + 'linie-mit-betriebspunkten.csv',
                                      delimiter=';')
        self.train_tracks_df = pd.read_csv(data_dir + 'zugzahlen.csv',
                                      delimiter=';')
        self.construction_df = pd.read_csv(data_dir + 'construction-site.csv',
                                      delimiter=';')

        # filter constructions without 'Umsetztung' or with 'Umleitung'
        self.construction_df = self.construction_df[self.construction_df['Umsetzung / \nIntervalltyp / Umleitung'].notnull()]
        self.construction_df = self.construction_df[self.construction_df['Umsetzung / \nIntervalltyp / Umleitung'] != "Umleitung"]

        # filter constructions without bp_from or without bp_to
        self.construction_df = self.construction_df[self.construction_df['bp_from'].notnull()]
        self.construction_df = self.construction_df[self.construction_df['bp_to'].notnull()]


        for index, row in self.operating_points_df.iterrows():
            id_word = row['Abbreviation of the operating point']

            self.points.setdefault(id_word,
                              Operating_point(index,
                                              id_word,
                                              (row['E'], row['N'])))
            self.points[id_word].add_line(row['LINIE'])

        op_index = 9000

        for index, row in self.train_tracks_df.iterrows():
            from_op = row['BP_Von_Abschnitt']
            to_op = row['BP_Bis_Abschnitt']

            for op in [from_op, to_op]:
                if op not in self.points.keys():
                    self.points.setdefault(op, Operating_point(op_index, from_op, (0,0)))
                    op_index += 1

            new_connection = Connection(from_op, to_op,
                                        row['Anzahl_Zuege'],
                                        row['Gesamtbelastung_Bruttotonnen'],
                                        row['Geschaeftscode'])
            self.points[from_op].add_connection_outbound(new_connection)
            self.points[to_op].add_connection_inbound(new_connection)


        """
        x_coords = []
        y_coords = []
        ids = []
        incidence_list = {}
        for point in self.points.values():
            ids.append(point.id_index)
            x_coords.append(point.gps[0])
            y_coords.append(point.gps[1])
            incidence_list[point.id_index] = []

            for connection in point.connections_outbound:
                incidence_list[point.id_index].append(self.points[connection.to_op].id_index)

        vis_data = {'ID': ids,
                'x': x_coords,
                'y': y_coords,
                'IL': incidence_list}
        """

    # returns a dict of Operation_point indexed by alphabetic op indices
    def get_operation_points_dict(self):
        return self.points

    # returns a list of Operation_point
    def get_operation_points_list(self):
        return list(self.points.values())

    # returns a list of Connection_congestions
    def get_connection_congestions_list(self):

        connection_congestions = {}

        # passenger congestion: capacity reduction during day
        for index, row in self.construction_df.iterrows():
            umsetzung = row['Umsetzung / \nIntervalltyp / Umleitung']
            if umsetzung not in ['Umsetzung', 'Sperre Strecke 24 Std', 'Sperre Strecke Tag']:
                continue # not during day
            from_op = row['bp_from']
            to_op = row['bp_to']

            if from_op not in self.points.keys() or to_op not in self.points.keys(): # location not known
                continue
            if from_op == to_op: # op congestion
                continue
            else: # connection congestion
                reduction_frac = row['reduction of capacity']
                if math.isnan(reduction_frac):
                    reduction_frac = 0

                # BFS starting at from_op
                frontier = [from_op]
                visited = set()
                visited.add(from_op)
                prev = {}
                while len(frontier) > 0:
                    element = frontier.pop(0)
                    if element == to_op:
                        break
                    for incident_connection in self.points[element].connections_outbound:
                        neighbor = incident_connection.to_op
                        if neighbor not in visited:
                            frontier.append(neighbor)
                            prev[neighbor] = element
                            visited.add(neighbor)
                    for incident_connection in self.points[element].connections_inbound:
                        neighbor = incident_connection.from_op
                        if neighbor not in visited and neighbor in self.points.keys():
                            frontier.append(neighbor)
                            prev[neighbor] = element
                            visited.add(neighbor)

                # backtracking
                assert(element == to_op) # check that a route was found
                route = [to_op]
                current = to_op
                while current in prev.keys():
                    current = prev[current]
                    route.append(current)

                # count total trains
                total_trains = 0
                for from_op in route:
                    for outbound_connection in self.points[from_op].connections_outbound:
                        to_op = outbound_connection.to_op
                        if to_op in route and outbound_connection.train_type == 'PERSONENVERKEHR':
                            trains = outbound_connection.trains
                            smaller_op = from_op if from_op <= to_op else to_op
                            greater_op = to_op if from_op <= to_op else from_op
                            connection_congestions.setdefault((smaller_op, greater_op),
                                                              Connection_congestion(smaller_op, greater_op))
                            connection_congestions[(smaller_op, greater_op)].congestion.increase_passenger_value(reduction_frac * trains)

        return list(connection_congestions.values())
