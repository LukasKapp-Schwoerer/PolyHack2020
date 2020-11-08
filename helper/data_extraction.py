import pandas as pd
import math
from datetime import date
from connect import *

class Congestion:
    def __init__(self, amount=0, passenger_trains=0, freight_trains=0):
        self.amount = amount 
        self.passenger_trains = passenger_trains
        self.freight_trains = freight_trains
        self.start_date = None
        self.end_date = None

    def __str__(self):
        return f"congestion amount: {self.amount}"

    def __add__(self, other):
        return Congestion(self.amount + other.amount,
                          self.passenger_trains + other.passenger_trains,
                          self.freight_trains + other.freight_trains)

    def zero(self):
        self.amount = 0
        self.start_date = None
        self.end_date = None

    def increase_amount(self, increment):
        self.amount+= increment

    def increase_passenger_trains(self, increment):
        self.passenger_trains += increment

    def increase_freight_trains(self, increment):
        self.freight_trains += increment

    def add_dates(self, d_start, d_end):
        # start_date
        if self.start_date == None:
            self.start_date = d_start
        else:
            self.start_date = min(d_start, self.start_date)
        # end_date
        if self.end_date == None:
            self.end_date = d_end
        else:
            self.end_date = max(d_start, self.end_date)

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
            trains = row['Anzahl_Zuege']

            abort = False
            for op in [from_op, to_op]:
                if op not in self.points.keys():
                    other_op = from_op if op != from_op else to_op
                    if other_op not in self.points.keys(): # both ops are outside of Switzerland
                        abort = True
                        continue
                    other_position = self.points[other_op].gps
                    self.points.setdefault(op, Operating_point(op_index, from_op, other_position))
                    """
                    other_position = self.points[other_op].gps
                    center = (2666281, 1210739) # center of Swizterland
                    delta = (other_position[0] - center[0], other_position[1] - center[1])
                    delta_length = math.sqrt(delta[0]**2 + delta[1]**2)
                    new_position = (other_position[0] + delta[0] / delta_length * 50000, other_position[1] + delta[1] / delta_length * 50000)
                    self.points.setdefault(op, Operating_point(op_index, from_op, new_position))
                    """
                    op_index += 1

            if abort: # both ops are outside of Switzerland
                continue

            new_connection = Connection(from_op, to_op, trains,
                                        row['Gesamtbelastung_Bruttotonnen'],
                                        row['Geschaeftscode'])
            self.points[from_op].add_connection_outbound(new_connection)
            self.points[to_op].add_connection_inbound(new_connection)
            if row['Geschaeftscode'] == 'PERSONENVERKEHR':
                self.points[from_op].congestion.increase_passenger_trains(trains)
                self.points[to_op].congestion.increase_passenger_trains(trains)
            else:
                self.points[from_op].congestion.increase_freight_trains(trains)
                self.points[to_op].congestion.increase_freight_trains(trains)


        # connect(self.points)
        

    # returns a dict of Operation_point indexed by alphabetic op indices
    def get_operation_points_dict(self):
        return self.points

    # returns a list of Operation_point
    def get_operation_points_list(self):
        return list(self.points.values())

    """
        returns a tuple (V, E), where
            V is a list of Operation_points that are congested
            E is a list of Connection_congestions
    """
    def get_congestions_list(self, range_date_start=date(2020, 1, 1), range_date_end=date(2050, 1, 1), is_daytime=True):

        connection_congestions = {}
        congested_vertices = []

        # zero congestion of vertices
        for point in self.points.values():
            point.congestion.zero()

        valid_umsetzung = ['Umsetzung', 'Sperre Strecke 24 Std', 'Sperre Bahnhof 24 Std']
        if is_daytime:
            valid_umsetzung += ['Sperre Strecke Tag', 'Sperre Bahnhof Tag']
            passenger_weight = 1
            freight_weight = 0.5
        else:
            valid_umsetzung += ['Sperre Strecke Nacht', 'Sperre Bahnhof Nacht']
            passenger_weight = 0.0
            freight_weight = 0.5

        for index, row in self.construction_df.iterrows():
            umsetzung = row['Umsetzung / \nIntervalltyp / Umleitung']
            if umsetzung not in valid_umsetzung:
                continue
            from_op = row['bp_from']
            to_op = row['bp_to']

            # get date from cc
            cc_date_start = row['date from']
            cc_date_end = row['date to']
            d_start = date(int(cc_date_start[0:4]), int(cc_date_start[5:7]), int(cc_date_start[8:10]))
            d_end = date(int(cc_date_end[0:4]), int(cc_date_end[5:7]), int(cc_date_end[8:10]))

            # check if in date range
            if not((range_date_start <= d_start <= range_date_end)
                    or (range_date_start <= d_end <= range_date_end)
                    or (d_start <= range_date_start and range_date_end <= d_end)):
                continue

            # start adding cc
            if from_op not in self.points.keys() or to_op not in self.points.keys(): # location not known
                continue

            reduction_frac = row['reduction of capacity']
            if math.isnan(reduction_frac):
                reduction_frac = 0

            if from_op == to_op: # op congestion
                trains = self.points[from_op].congestion.passenger_trains * passenger_weight + \
                         self.points[from_op].congestion.freight_trains * freight_weight

                congestion = self.points[from_op].congestion
                congestion.add_dates(d_start, d_end)

                congestion.increase_amount(reduction_frac * trains)
                congested_vertices.append(self.points[from_op])
                
            else: # connection congestion

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
                        if to_op in route :
                            trains = outbound_connection.trains
                            smaller_op = from_op if from_op <= to_op else to_op
                            greater_op = to_op if from_op <= to_op else from_op
                            if outbound_connection.train_type == 'PERSONENVERKEHR':
                                connection_congestions.setdefault((smaller_op, greater_op),
                                                                  Connection_congestion(smaller_op, greater_op))
                                connection_congestion = connection_congestions[(smaller_op, greater_op)]
                                connection_congestion.congestion.increase_passenger_trains(trains)
                                connection_congestion.congestion.increase_amount(reduction_frac * trains * passenger_weight)
                                connection_congestion.congestion.add_dates(d_start, d_end)
                            else:
                                connection_congestions.setdefault((smaller_op, greater_op),
                                                                  Connection_congestion(smaller_op, greater_op))
                                connection_congestion = connection_congestions[(smaller_op, greater_op)]
                                connection_congestion.congestion.increase_freight_trains(trains)
                                connection_congestion.congestion.increase_amount(reduction_frac * trains * freight_weight)
                                connection_congestion.congestion.add_dates(d_start, d_end)
                                
        return (congested_vertices, list(connection_congestions.values()))
