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
        racing_track = [[-7.3003, 0.66404, 2.22707, 0.13937],
[-7.1479, 0.91481, 2.22707, 0.13177],
[-6.99043, 1.14221, 2.22707, 0.1242],
[-6.82855, 1.34766, 2.22707, 0.11745],
[-6.66249, 1.53265, 2.22707, 0.11162],
[-6.4924, 1.69889, 2.22707, 0.1068],
[-6.31826, 1.84775, 2.22707, 0.10286],
[-6.14003, 1.98044, 2.22707, 0.09977],
[-5.95751, 2.09772, 2.22707, 0.09742],
[-5.77042, 2.20012, 2.22707, 0.09577],
[-5.57834, 2.28785, 2.22707, 0.09482],
[-5.3806, 2.36073, 2.32238, 0.09074],
[-5.17709, 2.42005, 2.41163, 0.0879],
[-4.96755, 2.4666, 2.42336, 0.08857],
[-4.75164, 2.50087, 2.24513, 0.09738],
[-4.52885, 2.52316, 2.09804, 0.10672],
[-4.29861, 2.53362, 1.97339, 0.11679],
[-4.06021, 2.53239, 1.86579, 0.12778],
[-3.81285, 2.5196, 1.77088, 0.13986],
[-3.55565, 2.49542, 1.68646, 0.15318],
[-3.28765, 2.46015, 1.60762, 0.16815],
[-3.00799, 2.41436, 1.5368, 0.1844],
[-2.71604, 2.35893, 1.5368, 0.19336],
[-2.41184, 2.29531, 1.5368, 0.20223],
[-2.09704, 2.22582, 1.5368, 0.20978],
[-1.77725, 2.1542, 1.5368, 0.21324],
[-1.45729, 2.08288, 1.5368, 0.21331],
[-1.13713, 2.01192, 1.5368, 0.21339],
[-0.8175, 1.9425, 1.5368, 0.21283],
[-0.50776, 1.8815, 1.5368, 0.20542],
[-0.21673, 1.83409, 1.5368, 0.19187],
[0.05272, 1.8023, 1.5368, 0.17655],
[0.30093, 1.78629, 1.5368, 0.16185],
[0.52961, 1.78532, 1.5368, 0.1488],
[0.7407, 1.79847, 1.5368, 0.13762],
[0.93605, 1.82482, 1.5368, 0.12827],
[1.11722, 1.86363, 1.5368, 0.12056],
[1.28544, 1.91442, 1.5368, 0.11434],
[1.44164, 1.97695, 1.5368, 0.10949],
[1.58647, 2.05131, 1.5368, 0.10593],
[1.72026, 2.13798, 1.53487, 0.10386],
[1.84304, 2.23805, 1.47286, 0.10754],
[1.95456, 2.35369, 1.42464, 0.11277],
[2.05803, 2.48223, 1.38599, 0.11906],
[2.15433, 2.62397, 1.36041, 0.12596],
[2.24429, 2.77954, 1.34806, 0.13331],
[2.3288, 2.95007, 1.34344, 0.14167],
[2.40912, 3.13762, 1.34344, 0.15187],
[2.48729, 3.34613, 1.34344, 0.16575],
[2.56614, 3.58148, 1.34344, 0.18476],
[2.64819, 3.84581, 1.34344, 0.20602],
[2.74538, 4.15231, 1.34344, 0.23934],
[2.84951, 4.45322, 1.34344, 0.23702],
[2.96535, 4.74339, 1.34344, 0.23257],
[3.096, 5.01492, 1.34344, 0.2243],
[3.23922, 5.2561, 1.34344, 0.20879],
[3.39081, 5.46104, 1.34344, 0.18975],
[3.55683, 5.63914, 1.34344, 0.18124],
[3.74302, 5.79321, 1.34344, 0.17989],
[3.94146, 5.91394, 1.34344, 0.1729],
[4.1412, 5.99654, 1.34344, 0.16089],
[4.33452, 6.04301, 1.34344, 0.148],
[4.51709, 6.05759, 1.34344, 0.13633],
[4.68675, 6.04489, 1.34344, 0.12664],
[4.84249, 6.00891, 1.34344, 0.11897],
[4.98391, 5.95299, 1.34344, 0.1132],
[5.11097, 5.87986, 1.34344, 0.10913],
[5.22364, 5.79157, 1.34951, 0.10607],
[5.32189, 5.68975, 1.34292, 0.10536],
[5.40564, 5.57568, 1.31882, 0.1073],
[5.47478, 5.4504, 1.30326, 0.10979],
[5.52923, 5.3148, 1.3, 0.1124],
[5.56887, 5.1696, 1.3, 0.11578],
[5.59377, 5.01552, 1.3, 0.12006],
[5.60389, 4.8531, 1.3, 0.12518],
[5.59957, 4.68299, 1.3, 0.1309],
[5.58163, 4.50598, 1.3, 0.13686],
[5.55158, 4.32309, 1.3, 0.14257],
[5.51175, 4.1356, 1.3, 0.14745],
[5.46539, 3.94509, 1.3, 0.15082],
[5.41108, 3.70844, 1.3, 0.18677],
[5.3692, 3.48, 1.3, 0.17866],
[5.34506, 3.26399, 1.3, 0.16719],
[5.34098, 3.0631, 1.3, 0.15456],
[5.3569, 2.87862, 1.3, 0.14244],
[5.39162, 2.71097, 1.3, 0.1317],
[5.44342, 2.56007, 1.3, 0.12272],
[5.51045, 2.42556, 1.3, 0.11561],
[5.59116, 2.30716, 1.3, 0.11022],
[5.68414, 2.20466, 1.3, 0.10645],
[5.78824, 2.11798, 1.3, 0.1042],
[5.90255, 2.04735, 1.3, 0.10337],
[6.02637, 1.99323, 1.30988, 0.10316],
[6.1591, 1.95634, 1.32549, 0.10393],
[6.30037, 1.93794, 1.3539, 0.10522],
[6.44988, 1.93968, 1.38673, 0.10783],
[6.60757, 1.9642, 1.39509, 0.11439],
[6.77358, 2.01557, 1.39509, 0.12457],
[6.94831, 2.10007, 1.39509, 0.13912],
[7.13276, 2.2292, 1.39509, 0.16139],
[7.34458, 2.33047, 1.39509, 0.16829],
[7.54824, 2.3882, 1.39509, 0.15173],
[7.74219, 2.40994, 1.39509, 0.1399],
[7.92546, 2.40121, 1.39509, 0.13152],
[8.09714, 2.36565, 1.39509, 0.12567],
[8.2563, 2.30589, 1.39509, 0.12186],
[8.40193, 2.22392, 1.39509, 0.11979],
[8.5329, 2.12129, 1.40285, 0.11862],
[8.64792, 1.9992, 1.41685, 0.11838],
[8.74533, 1.85858, 1.43676, 0.11906],
[8.82313, 1.70019, 1.47305, 0.11979],
[8.87912, 1.52496, 1.50943, 0.12187],
[8.91042, 1.33373, 1.55823, 0.12435],
[8.91375, 1.12773, 1.61441, 0.12762],
[8.88532, 0.90866, 1.68164, 0.13136],
[8.82103, 0.67916, 1.76414, 0.1351],
[8.71714, 0.44305, 1.85079, 0.13937],
[8.57041, 0.20563, 1.95568, 0.14272],
[8.37981, -0.02632, 2.07674, 0.14456],
[8.1475, -0.24517, 2.22433, 0.14349],
[7.87973, -0.44398, 2.39604, 0.13919],
[7.58598, -0.61784, 2.61285, 0.13064],
[7.27664, -0.7656, 2.89614, 0.11837],
[6.95831, -0.89026, 3.20182, 0.10677],
[6.63404, -0.99565, 3.34432, 0.10195],
[6.30519, -1.08322, 3.50032, 0.09722],
[5.97297, -1.15441, 3.67943, 0.09234],
[5.63861, -1.21064, 3.87771, 0.08744],
[5.30352, -1.25334, 4.0, 0.08445],
[4.96906, -1.28399, 4.0, 0.08397],
[4.63607, -1.30413, 4.0, 0.0834],
[4.30471, -1.31533, 4.0, 0.08289],
[3.97475, -1.31908, 4.0, 0.0825],
[3.64581, -1.31678, 4.0, 0.08224],
[3.31757, -1.30975, 4.0, 0.08208],
[2.98977, -1.2993, 4.0, 0.08199],
[2.73271, -1.2896, 4.0, 0.06431],
[2.48975, -1.28128, 4.0, 0.06078],
[2.25393, -1.2737, 4.0, 0.05898],
[2.02351, -1.26659, 3.94851, 0.05838],
[1.80296, -1.259, 3.24317, 0.06804],
[1.58717, -1.2504, 2.80596, 0.07697],
[1.37504, -1.24035, 2.52262, 0.08419],
[1.1657, -1.22848, 2.30755, 0.09087],
[0.95842, -1.21446, 2.15486, 0.09641],
[0.75259, -1.19797, 2.03608, 0.10142],
[0.54765, -1.17872, 1.94575, 0.10579],
[0.34316, -1.15647, 1.87407, 0.10976],
[0.13874, -1.13101, 1.82331, 0.11298],
[-0.06593, -1.10213, 1.78658, 0.11569],
[-0.27111, -1.06969, 1.76515, 0.11768],
[-0.477, -1.03355, 1.75729, 0.11896],
[-0.6838, -0.99359, 1.75729, 0.11986],
[-0.89164, -0.94974, 1.75729, 0.12087],
[-1.10063, -0.90192, 1.75729, 0.122],
[-1.31087, -0.85006, 1.75729, 0.12323],
[-1.52245, -0.79409, 1.75729, 0.12454],
[-1.73543, -0.73392, 1.75729, 0.12595],
[-1.9499, -0.66946, 1.75729, 0.12744],
[-2.16593, -0.60058, 1.75729, 0.12903],
[-2.39313, -0.53467, 1.75729, 0.13462],
[-2.61318, -0.48004, 1.75729, 0.12902],
[-2.82481, -0.43857, 1.75729, 0.12272],
[-3.0274, -0.41105, 1.75729, 0.11634],
[-3.22067, -0.39774, 1.75729, 0.11024],
[-3.40467, -0.39836, 1.75729, 0.10471],
[-3.57962, -0.41242, 1.75729, 0.09988],
[-3.74578, -0.43935, 1.75729, 0.09579],
[-3.9034, -0.47862, 1.75729, 0.09244],
[-4.05275, -0.52971, 1.75729, 0.08982],
[-4.19406, -0.59218, 1.75729, 0.08792],
[-4.32751, -0.66571, 1.75729, 0.08671],
[-4.45328, -0.75007, 1.76214, 0.08594],
[-4.57151, -0.84516, 1.77765, 0.08535],
[-4.6823, -0.95107, 1.80358, 0.08498],
[-4.78571, -1.06812, 1.72451, 0.09057],
[-4.88169, -1.19702, 1.62518, 0.09889],
[-4.97015, -1.33878, 1.54512, 0.10815],
[-5.05092, -1.49471, 1.49036, 0.11783],
[-5.12338, -1.66663, 1.45275, 0.12842],
[-5.18639, -1.85598, 1.42673, 0.13987],
[-5.23804, -2.06196, 1.41176, 0.15042],
[-5.27638, -2.27921, 1.40869, 0.1566],
[-5.30074, -2.5002, 1.40869, 0.15783],
[-5.31247, -2.72014, 1.40869, 0.15636],
[-5.31359, -2.93773, 1.40869, 0.15446],
[-5.30613, -3.15316, 1.40869, 0.15302],
[-5.29187, -3.36693, 1.40869, 0.15209],
[-5.27244, -3.57949, 1.40869, 0.15152],
[-5.24945, -3.79124, 1.40869, 0.1512],
[-5.2245, -4.00212, 1.40869, 0.15074],
[-5.20742, -4.19296, 1.40869, 0.13602],
[-5.19929, -4.37483, 1.40869, 0.12923],
[-5.20174, -4.54747, 1.40869, 0.12257],
[-5.21578, -4.71063, 1.40869, 0.11626],
[-5.2417, -4.86432, 1.40869, 0.11064],
[-5.27971, -5.00838, 1.40869, 0.10576],
[-5.32969, -5.14275, 1.40869, 0.10177],
[-5.39152, -5.26724, 1.40869, 0.09867],
[-5.46497, -5.38166, 1.40869, 0.09652],
[-5.54986, -5.48573, 1.40869, 0.09534],
[-5.64609, -5.579, 1.40869, 0.09514],
[-5.75372, -5.66081, 1.40869, 0.09596],
[-5.87285, -5.73028, 1.41765, 0.09728],
[-6.00372, -5.78628, 1.42929, 0.09959],
[-6.14677, -5.8271, 1.45318, 0.10237],
[-6.30252, -5.85053, 1.48554, 0.10602],
[-6.47144, -5.8536, 1.53058, 0.11038],
[-6.65367, -5.83252, 1.58051, 0.11607],
[-6.8485, -5.78241, 1.63545, 0.12301],
[-7.05294, -5.69795, 1.70146, 0.13001],
[-7.25958, -5.57603, 1.7722, 0.13538],
[-7.45618, -5.41974, 1.85187, 0.13562],
[-7.6313, -5.23881, 1.9428, 0.1296],
[-7.78099, -5.0427, 2.04508, 0.12064],
[-7.9073, -4.8359, 2.15559, 0.11242],
[-8.01359, -4.61923, 2.28468, 0.10563],
[-8.10257, -4.3923, 2.43016, 0.1003],
[-8.17607, -4.1545, 2.56777, 0.09693],
[-8.235, -3.90485, 2.49188, 0.10294],
[-8.27922, -3.64159, 2.43704, 0.10954],
[-8.3081, -3.36251, 2.37711, 0.11803],
[-8.32044, -3.06552, 2.32906, 0.12762],
[-8.31469, -2.75083, 2.28057, 0.13801],
[-8.29005, -2.4258, 2.22707, 0.14636],
[-8.24771, -2.09986, 2.22707, 0.14758],
[-8.18953, -1.77628, 2.22707, 0.14762],
[-8.11721, -1.45568, 2.22707, 0.14758],
[-8.03229, -1.1382, 2.22707, 0.14757],
[-7.93579, -0.82398, 2.22707, 0.1476],
[-7.82863, -0.51308, 2.22707, 0.14766],
[-7.71173, -0.2055, 2.22707, 0.14775],
[-7.5844, 0.09757, 2.22707, 0.14761],
[-7.44646, 0.39021, 2.22707, 0.14527]]

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
