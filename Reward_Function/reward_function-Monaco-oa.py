import math


class Reward:
    def __init__(self, verbose=False):
        self.first_racingpoint_index = None
        self.verbose = verbose

    def reward_function(self, params):

        # Import package (needed for heading)
        import math

        ################## HELPER FUNCTIONS ###################

        def dist_2_points(x1, x2, y1, y2):
            return abs(abs(x1-x2)**2 + abs(y1-y2)**2)**0.5

        def closest_2_racing_points_index(racing_coords, car_coords):

            # Calculate all distances to racing points
            distances = []
            for i in range(len(racing_coords)):
                distance = dist_2_points(x1=racing_coords[i][0], x2=car_coords[0],
                                         y1=racing_coords[i][1], y2=car_coords[1])
                distances.append(distance)

            # Get index of the closest racing point
            closest_index = distances.index(min(distances))

            # Get index of the second closest racing point
            distances_no_closest = distances.copy()
            distances_no_closest[closest_index] = 999
            second_closest_index = distances_no_closest.index(
                min(distances_no_closest))

            return [closest_index, second_closest_index]

        def dist_to_racing_line(closest_coords, second_closest_coords, car_coords):
            
            # Calculate the distances between 2 closest racing points
            a = abs(dist_2_points(x1=closest_coords[0],
                                  x2=second_closest_coords[0],
                                  y1=closest_coords[1],
                                  y2=second_closest_coords[1]))

            # Distances between car and closest and second closest racing point
            b = abs(dist_2_points(x1=car_coords[0],
                                  x2=closest_coords[0],
                                  y1=car_coords[1],
                                  y2=closest_coords[1]))
            c = abs(dist_2_points(x1=car_coords[0],
                                  x2=second_closest_coords[0],
                                  y1=car_coords[1],
                                  y2=second_closest_coords[1]))

            # Calculate distance between car and racing line (goes through 2 closest racing points)
            # try-except in case a=0 (rare bug in DeepRacer)
            try:
                distance = abs(-(a**4) + 2*(a**2)*(b**2) + 2*(a**2)*(c**2) -
                               (b**4) + 2*(b**2)*(c**2) - (c**4))**0.5 / (2*a)
            except:
                distance = b

            return distance

        # Calculate which one of the closest racing points is the next one and which one the previous one
        def next_prev_racing_point(closest_coords, second_closest_coords, car_coords, heading):

            # Virtually set the car more into the heading direction
            heading_vector = [math.cos(math.radians(
                heading)), math.sin(math.radians(heading))]
            new_car_coords = [car_coords[0]+heading_vector[0],
                              car_coords[1]+heading_vector[1]]

            # Calculate distance from new car coords to 2 closest racing points
            distance_closest_coords_new = dist_2_points(x1=new_car_coords[0],
                                                        x2=closest_coords[0],
                                                        y1=new_car_coords[1],
                                                        y2=closest_coords[1])
            distance_second_closest_coords_new = dist_2_points(x1=new_car_coords[0],
                                                               x2=second_closest_coords[0],
                                                               y1=new_car_coords[1],
                                                               y2=second_closest_coords[1])

            if distance_closest_coords_new <= distance_second_closest_coords_new:
                next_point_coords = closest_coords
                prev_point_coords = second_closest_coords
            else:
                next_point_coords = second_closest_coords
                prev_point_coords = closest_coords

            return [next_point_coords, prev_point_coords]

        def racing_direction_diff(closest_coords, second_closest_coords, car_coords, heading):

            # Calculate the direction of the center line based on the closest waypoints
            next_point, prev_point = next_prev_racing_point(closest_coords,
                                                            second_closest_coords,
                                                            car_coords,
                                                            heading)

            # Calculate the direction in radius, arctan2(dy, dx), the result is (-pi, pi) in radians
            track_direction = math.atan2(
                next_point[1] - prev_point[1], next_point[0] - prev_point[0])

            # Convert to degree
            track_direction = math.degrees(track_direction)

            # Calculate the difference between the track direction and the heading direction of the car
            direction_diff = abs(track_direction - heading)
            if direction_diff > 180:
                direction_diff = 360 - direction_diff

            return direction_diff

        # Gives back indexes that lie between start and end index of a cyclical list 
        # (start index is included, end index is not)
        def indexes_cyclical(start, end, array_len):

            if end < start:
                end += array_len

            return [index % array_len for index in range(start, end)]

        # Calculate how long car would take for entire lap, if it continued like it did until now
        def projected_time(first_index, closest_index, step_count, times_list):

            # Calculate how much time has passed since start
            current_actual_time = (step_count-1) / 15

            # Calculate which indexes were already passed
            indexes_traveled = indexes_cyclical(first_index, closest_index, len(times_list))

            # Calculate how much time should have passed if car would have followed optimals
            current_expected_time = sum([times_list[i] for i in indexes_traveled])

            # Calculate how long one entire lap takes if car follows optimals
            total_expected_time = sum(times_list)

            # Calculate how long car would take for entire lap, if it continued like it did until now
            try:
                projected_time = (current_actual_time/current_expected_time) * total_expected_time
            except:
                projected_time = 9999

            return projected_time

        #################### RACING LINE ######################

        # Optimal racing line for the Spain track
        # Each row: [x,y,speed,timeFromPreviousPoint]
        racing_track = [[-7.3003, 0.66404, 1.3, 0.23876],
[-7.1479, 0.91481, 1.3, 0.22573],
[-6.99043, 1.14221, 1.3, 0.21276],
[-6.82855, 1.34766, 1.3, 0.20121],
[-6.66249, 1.53265, 1.3, 0.19122],
[-6.4924, 1.69889, 1.3, 0.18295],
[-6.31826, 1.84775, 1.3, 0.17622],
[-6.14003, 1.98044, 1.3, 0.17092],
[-5.95751, 2.09772, 1.3, 0.16689],
[-5.77042, 2.20012, 1.3, 0.16406],
[-5.57834, 2.28785, 1.3, 0.16244],
[-5.3806, 2.36073, 1.3, 0.16211],
[-5.17709, 2.42005, 1.3, 0.16306],
[-4.96755, 2.4666, 1.3, 0.16511],
[-4.75164, 2.50087, 1.3, 0.16817],
[-4.52885, 2.52316, 1.3, 0.17223],
[-4.29861, 2.53362, 1.3, 0.17729],
[-4.06021, 2.53239, 1.3, 0.18339],
[-3.81285, 2.5196, 1.3, 0.19052],
[-3.55565, 2.49542, 1.3, 0.19872],
[-3.48381, 2.14935, 1.43982, 0.24548],
[-3.16408, 2.07339, 1.51261, 0.21726],
[-2.84361, 1.99548, 1.51261, 0.21803],
[-2.52352, 1.91701, 1.51261, 0.21788],
[-2.20189, 1.83725, 1.51261, 0.21907],
[-1.87516, 1.75711, 1.51261, 0.22241],
[-1.54203, 1.68126, 1.51261, 0.22587],
[-1.20375, 1.61524, 1.51261, 0.22786],
[-0.86534, 1.56278, 1.51261, 0.2264],
[-0.53607, 1.52262, 1.51261, 0.2193],
[-0.22537, 1.48623, 1.51261, 0.20681],
[0.08627, 1.4295, 1.51261, 0.20941],
[0.39331, 1.35167, 1.51261, 0.20941],
[0.73585, 1.24122, 1.51261, 0.23794],
[1.07982, 1.13869, 1.51261, 0.23728],
[0.93605, 1.82482, 1.53859, 0.45563],
[1.11722, 1.86363, 1.84006, 0.10069],
[1.28544, 1.91442, 1.84006, 0.0955],
[1.44164, 1.97695, 1.84006, 0.09144],
[1.58647, 2.05131, 1.84006, 0.08847],
[1.72026, 2.13798, 1.84006, 0.08663],
[1.84304, 2.23805, 1.84006, 0.08608],
[1.95456, 2.35369, 1.84006, 0.08731],
[2.05803, 2.48223, 1.84006, 0.08968],
[2.15433, 2.62397, 1.84006, 0.09313],
[2.24429, 2.77954, 1.84006, 0.09766],
[2.3288, 2.95007, 1.84006, 0.10343],
[2.40912, 3.13762, 1.78277, 0.11445],
[2.48729, 3.34613, 1.78277, 0.1249],
[2.56614, 3.58148, 1.78277, 0.13923],
[2.64819, 3.84581, 1.78277, 0.15525],
[2.74538, 4.15231, 1.78277, 0.18036],
[2.84951, 4.45322, 1.78277, 0.17861],
[2.55936, 5.11544, 1.78277, 0.40555],
[2.79532, 5.38861, 1.78277, 0.20248],
[3.03924, 5.6552, 1.78277, 0.20268],
[3.28216, 5.92855, 1.78277, 0.20512],
[3.28216, 5.92855, 1.78277, 0.0],
[3.51425, 6.18381, 1.78277, 0.19352],
[3.75526, 6.41354, 1.78277, 0.18677],
[4.01376, 6.60111, 1.78277, 0.17915],
[4.29534, 6.73253, 1.78277, 0.1743],
[4.59907, 6.81552, 1.78277, 0.17661],
[4.91114, 6.82762, 1.78277, 0.17518],
[5.21342, 6.78787, 1.78277, 0.17102],
[5.48438, 6.70271, 1.78277, 0.15932],
[5.73611, 6.5708, 1.78277, 0.15941],
[5.93409, 6.41981, 1.78277, 0.13966],
[5.32189, 5.68975, 1.82846, 0.52108],
[5.40564, 5.57568, 1.85148, 0.07643],
[5.47478, 5.4504, 1.8256, 0.07838],
[5.52923, 5.3148, 1.8256, 0.08004],
[5.56887, 5.1696, 1.8256, 0.08244],
[5.59377, 5.01552, 1.8256, 0.0855],
[5.60389, 4.8531, 1.8256, 0.08914],
[5.59957, 4.68299, 1.8256, 0.09321],
[5.58163, 4.50598, 1.8256, 0.09746],
[5.55158, 4.32309, 1.73777, 0.10665],
[5.51175, 4.1356, 1.73777, 0.1103],
[5.46539, 3.94509, 1.73777, 0.11282],
[5.41108, 3.70844, 1.73777, 0.13972],
[5.3692, 3.48, 1.73777, 0.13365],
[5.34506, 3.26399, 1.73777, 0.12508],
[5.35894, 2.89689, 1.73777, 0.2114],
[5.33674, 2.68787, 1.73777, 0.12095],
[5.33119, 2.4947, 1.73777, 0.1112],
[5.34229, 2.32022, 1.73777, 0.10061],
[5.37297, 2.1721, 1.73777, 0.08705],
[5.42447, 2.04744, 1.73777, 0.07762],
[5.4979, 1.94318, 1.73777, 0.07338],
[5.59132, 1.86168, 1.73777, 0.07134],
[5.69883, 1.80612, 1.73777, 0.06964],
[5.82461, 1.77427, 1.73777, 0.07467],
[5.95899, 1.77059, 1.73777, 0.07736],
[6.09173, 1.79551, 1.73777, 0.07772],
[6.23439, 1.85206, 1.73777, 0.08831],
[6.38328, 1.94452, 1.73777, 0.10085],
[6.53789, 2.0824, 1.73777, 0.11921],
[6.94831, 2.10007, 1.92769, 0.2131],
[7.13276, 2.2292, 2.67638, 0.08413],
[7.34458, 2.33047, 1.80064, 0.13039],
[7.54824, 2.3882, 1.80064, 0.11756],
[7.74219, 2.40994, 1.80064, 0.10839],
[7.92546, 2.40121, 1.80064, 0.1019],
[8.09714, 2.36565, 1.80064, 0.09737],
[8.2563, 2.30589, 1.80064, 0.09441],
[8.40193, 2.22392, 1.80064, 0.09281],
[8.5329, 2.12129, 1.80064, 0.09241],
[8.64792, 1.9992, 1.80064, 0.09315],
[8.74533, 1.85858, 1.80064, 0.095],
[8.82313, 1.70019, 1.80064, 0.098],
[8.87912, 1.52496, 1.80064, 0.10216],
[8.91042, 1.33373, 1.80064, 0.10761],
[8.91375, 1.12773, 1.80064, 0.11442],
[8.88532, 0.90866, 1.80064, 0.12268],
[8.82103, 0.67916, 1.80064, 0.13236],
[8.71714, 0.44305, 1.7615, 0.14644],
[8.57041, 0.20563, 1.7615, 0.15845],
[8.37981, -0.02632, 1.7615, 0.17043],
[8.1475, -0.24517, 1.7615, 0.18119],
[7.87973, -0.44398, 1.7615, 0.18933],
[7.4183, -0.3522, 1.7615, 0.26709],
[7.14404, -0.54306, 1.7615, 0.18969],
[6.85759, -0.69662, 1.7615, 0.18451],
[6.55151, -0.80817, 1.7615, 0.18494],
[6.23389, -0.88322, 1.7615, 0.18528],
[5.91637, -0.94432, 1.7615, 0.18356],
[5.5957, -0.97556, 1.7615, 0.18291],
[5.27311, -0.97187, 1.7615, 0.18315],
[4.94623, -0.9318, 1.7615, 0.18696],
[4.62162, -0.92632, 1.7615, 0.1843],
[4.29961, -0.96231, 1.7615, 0.18395],
[3.98099, -1.04266, 1.7615, 0.18654],
[3.65696, -1.09792, 1.7615, 0.18661],
[3.33942, -1.1098, 1.7615, 0.18039],
[3.02219, -1.09058, 1.7615, 0.18042],
[2.73271, -1.2896, 1.7615, 0.19943],
[2.48975, -1.28128, 4.0, 0.06078],
[2.25393, -1.2737, 4.0, 0.05898],
[2.02351, -1.26659, 4.0, 0.05763],
[1.80296, -1.259, 1.77698, 0.12418],
[1.58717, -1.2504, 1.77698, 0.12154],
[1.37504, -1.24035, 1.77698, 0.11951],
[1.1657, -1.22848, 1.77698, 0.118],
[0.95842, -1.21446, 1.77698, 0.11691],
[0.75259, -1.19797, 1.77698, 0.11621],
[0.54765, -1.17872, 1.77698, 0.11584],
[0.34316, -1.15647, 1.77698, 0.11576],
[0.13874, -1.13101, 1.77698, 0.11593],
[-0.06593, -1.10213, 1.77698, 0.11632],
[-0.27111, -1.06969, 1.77698, 0.1169],
[-0.477, -1.03355, 1.77698, 0.11764],
[-0.6838, -0.99359, 1.77698, 0.11853],
[-0.89164, -0.94974, 1.77698, 0.11954],
[-1.10063, -0.90192, 1.77698, 0.12065],
[-1.31087, -0.85006, 1.61017, 0.13449],
[-1.52245, -0.79409, 1.5451, 0.14164],
[-1.73543, -0.73392, 1.5451, 0.14324],
[-1.9499, -0.66946, 1.5451, 0.14494],
[-2.16593, -0.60058, 1.5451, 0.14675],
[-2.39313, -0.53467, 1.5451, 0.15311],
[-2.60098, 0.05608, 1.5451, 0.40531],
[-2.90706, 0.17029, 1.5451, 0.21144],
[-3.16857, 0.24573, 1.5451, 0.17615],
[-3.41824, 0.29329, 1.5451, 0.1645],
[-3.65687, 0.31565, 1.5451, 0.15512],
[-3.88454, 0.31053, 1.5451, 0.14739],
[-4.10284, 0.2805, 1.5451, 0.14261],
[-4.31003, 0.22456, 1.5451, 0.1389],
[-4.50573, 0.14443, 1.5451, 0.13687],
[-4.68934, 0.0393, 1.5451, 0.13693],
[-4.85584, -0.08528, 1.5451, 0.13459],
[-5.00303, -0.22526, 1.5451, 0.13146],
[-5.13292, -0.38035, 1.5451, 0.13093],
[-5.24134, -0.54876, 1.5451, 0.12963],
[-5.32599, -0.72649, 1.5451, 0.12741],
[-4.88169, -1.19702, 1.5451, 0.41884],
[-4.97015, -1.33878, 1.89579, 0.08814],
[-5.05092, -1.49471, 1.89579, 0.09263],
[-5.12338, -1.66663, 1.89579, 0.09841],
[-5.18639, -1.85598, 1.89579, 0.10526],
[-5.23804, -2.06196, 1.89579, 0.11201],
[-5.27638, -2.27921, 1.89579, 0.11637],
[-5.30074, -2.5002, 1.89579, 0.11728],
[-5.31247, -2.72014, 1.89579, 0.11618],
[-5.31359, -2.93773, 1.89579, 0.11477],
[-5.30613, -3.15316, 1.89579, 0.11371],
[-5.29187, -3.36693, 1.89579, 0.11301],
[-5.27244, -3.57949, 1.89579, 0.11259],
[-5.24945, -3.79124, 1.89579, 0.11235],
[-5.2245, -4.00212, 1.89579, 0.11201],
[-5.20742, -4.19296, 1.89579, 0.10107],
[-5.19929, -4.37483, 1.52315, 0.11952],
[-5.20174, -4.54747, 1.52315, 0.11336],
[-5.21578, -4.71063, 1.52315, 0.10752],
[-5.2417, -4.86432, 1.52315, 0.10233],
[-5.27971, -5.00838, 1.52315, 0.09782],
[-5.32969, -5.14275, 1.52315, 0.09412],
[-4.5854, -5.77664, 1.52315, 0.64186],
[-4.68098, -5.98965, 1.52315, 0.15328],
[-4.80602, -6.174, 1.52315, 0.14624],
[-4.95194, -6.33567, 1.52315, 0.14299],
[-5.12061, -6.47255, 1.52315, 0.14261],
[-5.31347, -6.57886, 1.52315, 0.14458],
[-5.53349, -6.64643, 1.52315, 0.15111],
[-5.77588, -6.67789, 1.52315, 0.16047],
[-6.04627, -6.66664, 1.52315, 0.17768],
[-6.33983, -6.60273, 1.52315, 0.19724],
[-6.64672, -6.47427, 1.52315, 0.21842],
[-6.97288, -6.2842, 1.52315, 0.24784],
[-7.25456, -6.10812, 1.52315, 0.2181],
[-7.53566, -5.93062, 1.52315, 0.21826],
[-7.83114, -5.7411, 1.52315, 0.23046],
[-7.6313, -5.23881, 1.63172, 0.3313],
[-7.78099, -5.0427, 3.92334, 0.06288],
[-7.9073, -4.8359, 4.0, 0.06058],
[-8.01359, -4.61923, 4.0, 0.06033],
[-8.10257, -4.3923, 4.0, 0.06094],
[-8.17607, -4.1545, 4.0, 0.06223],
[-8.235, -3.90485, 4.0, 0.06413],
[-8.27922, -3.64159, 4.0, 0.06674],
[-8.3081, -3.36251, 4.0, 0.07014],
[-8.32044, -3.06552, 4.0, 0.07431],
[-8.31469, -2.75083, 4.0, 0.07869],
[-8.29005, -2.4258, 4.0, 0.08149],
[-8.24771, -2.09986, 4.0, 0.08217],
[-8.18953, -1.77628, 4.0, 0.08219],
[-8.11721, -1.45568, 4.0, 0.08217],
[-8.03229, -1.1382, 4.0, 0.08216],
[-7.93579, -0.82398, 4.0, 0.08218],
[-7.82863, -0.51308, 4.0, 0.08221],
[-7.71173, -0.2055, 4.0, 0.08226],
[-7.5844, 0.09757, 4.0, 0.08218],
[-7.44646, 0.39021, 1.3, 0.24887]]

        ################## INPUT PARAMETERS ###################

        # Read all input parameters
        all_wheels_on_track = params['all_wheels_on_track']
        x = params['x']
        y = params['y']
        distance_from_center = params['distance_from_center']
        is_left_of_center = params['is_left_of_center']
        heading = params['heading']
        progress = params['progress']
        steps = params['steps']
        speed = params['speed']
        steering_angle = params['steering_angle']
        track_width = params['track_width']
        waypoints = params['waypoints']
        closest_waypoints = params['closest_waypoints']
        is_offtrack = params['is_offtrack']

        ############### OPTIMAL X,Y,SPEED,TIME ################

        # Get closest indexes for racing line (and distances to all points on racing line)
        closest_index, second_closest_index = closest_2_racing_points_index(
            racing_track, [x, y])

        # Get optimal [x, y, speed, time] for closest and second closest index
        optimals = racing_track[closest_index]
        optimals_second = racing_track[second_closest_index]

        # Save first racingpoint of episode for later
        if self.verbose == True:
            self.first_racingpoint_index = 0 # this is just for testing purposes
        if steps == 1:
            self.first_racingpoint_index = closest_index

        ################ REWARD AND PUNISHMENT ################

        ## Define the default reward ##
        reward = 1

        ## Reward if car goes close to optimal racing line ##
        DISTANCE_MULTIPLE = 1
        dist = dist_to_racing_line(optimals[0:2], optimals_second[0:2], [x, y])
        distance_reward = max(1e-3, 1 - (dist/(track_width*0.5)))
        reward += distance_reward * DISTANCE_MULTIPLE

        ## Reward if speed is close to optimal speed ##
        SPEED_DIFF_NO_REWARD = 1
        SPEED_MULTIPLE = 2
        speed_diff = abs(optimals[2]-speed)
        if speed_diff <= SPEED_DIFF_NO_REWARD:
            # we use quadratic punishment (not linear) bc we're not as confident with the optimal speed
            # so, we do not punish small deviations from optimal speed
            speed_reward = (1 - (speed_diff/(SPEED_DIFF_NO_REWARD))**2)**2
        else:
            speed_reward = 0
        reward += speed_reward * SPEED_MULTIPLE

        # Reward if less steps
        REWARD_PER_STEP_FOR_FASTEST_TIME = 1 
        STANDARD_TIME = 37
        FASTEST_TIME = 27
        times_list = [row[3] for row in racing_track]
        projected_time = projected_time(self.first_racingpoint_index, closest_index, steps, times_list)
        try:
            steps_prediction = projected_time * 15 + 1
            reward_prediction = max(1e-3, (-REWARD_PER_STEP_FOR_FASTEST_TIME*(FASTEST_TIME) /
                                           (STANDARD_TIME-FASTEST_TIME))*(steps_prediction-(STANDARD_TIME*15+1)))
            steps_reward = min(REWARD_PER_STEP_FOR_FASTEST_TIME, reward_prediction / steps_prediction)
        except:
            steps_reward = 0
        reward += steps_reward

        # Zero reward if obviously wrong direction (e.g. spin)
        direction_diff = racing_direction_diff(
            optimals[0:2], optimals_second[0:2], [x, y], heading)
        if direction_diff > 30:
            reward = 1e-3
            
        # Zero reward of obviously too slow
        speed_diff_zero = optimals[2]-speed
        if speed_diff_zero > 0.5:
            reward = 1e-3
            
        ## Incentive for finishing the lap in less steps ##
        REWARD_FOR_FASTEST_TIME = 1500 # should be adapted to track length and other rewards
        STANDARD_TIME = 37  # seconds (time that is easily done by model)
        FASTEST_TIME = 27  # seconds (best time of 1st place on the track)
        if progress == 100:
            finish_reward = max(1e-3, (-REWARD_FOR_FASTEST_TIME /
                      (15*(STANDARD_TIME-FASTEST_TIME)))*(steps-STANDARD_TIME*15))
        else:
            finish_reward = 0
        reward += finish_reward
        
        ## Zero reward if off track ##
        if all_wheels_on_track == False:
            reward = 1e-3

        ####################### VERBOSE #######################
        
        if self.verbose == True:
            print("Closest index: %i" % closest_index)
            print("Distance to racing line: %f" % dist)
            print("=== Distance reward (w/out multiple): %f ===" % (distance_reward))
            print("Optimal speed: %f" % optimals[2])
            print("Speed difference: %f" % speed_diff)
            print("=== Speed reward (w/out multiple): %f ===" % speed_reward)
            print("Direction difference: %f" % direction_diff)
            print("Predicted time: %f" % projected_time)
            print("=== Steps reward: %f ===" % steps_reward)
            print("=== Finish reward: %f ===" % finish_reward)
            
        #################### RETURN REWARD ####################
        
        # Always return a float value
        return float(reward)


reward_object = Reward() # add parameter verbose=True to get noisy output for testing


def reward_function(params):
    return reward_object.reward_function(params)
