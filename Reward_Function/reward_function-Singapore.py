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
        racing_track = [[8.12432, 0.98849, 1.96764, 0.12537],
[8.08638, 1.23224, 1.8642, 0.13233],
[8.04844, 1.47599, 1.77769, 0.13877],
[8.0105, 1.71974, 1.69896, 0.1452],
[7.9727, 1.96351, 1.62855, 0.15147],
[7.93404, 2.20513, 1.56984, 0.15587],
[7.89354, 2.44306, 1.52327, 0.15844],
[7.85035, 2.67579, 1.48349, 0.15956],
[7.80376, 2.90208, 1.45006, 0.15933],
[7.7532, 3.12095, 1.43007, 0.15708],
[7.69824, 3.33174, 1.41647, 0.15379],
[7.63858, 3.53406, 1.41241, 0.14935],
[7.574, 3.72775, 1.41241, 0.14455],
[7.50433, 3.91277, 1.41241, 0.13998],
[7.42941, 4.08919, 1.41241, 0.13571],
[7.34906, 4.25715, 1.41241, 0.13182],
[7.26308, 4.41684, 1.41241, 0.12841],
[7.17118, 4.56844, 1.41241, 0.12552],
[7.07292, 4.71217, 1.41241, 0.12326],
[6.96769, 4.84824, 1.41241, 0.12179],
[6.85423, 4.97677, 1.41241, 0.12138],
[6.73022, 5.0982, 1.41241, 0.12288],
[6.59076, 5.21371, 1.41241, 0.12822],
[6.42891, 5.32317, 1.41241, 0.13834],
[6.24719, 5.41813, 1.41241, 0.14517],
[6.06397, 5.48675, 1.41241, 0.13852],
[5.88703, 5.52882, 1.41241, 0.12877],
[5.71828, 5.54744, 1.41241, 0.1202],
[5.55802, 5.54546, 1.41241, 0.11348],
[5.40622, 5.525, 1.41241, 0.10845],
[5.26281, 5.48776, 1.41241, 0.10491],
[5.12782, 5.43492, 1.41241, 0.10264],
[5.0014, 5.36732, 1.4147, 0.10133],
[4.88384, 5.28555, 1.42596, 0.10043],
[4.77555, 5.18999, 1.44837, 0.09972],
[4.67703, 5.08089, 1.47422, 0.09971],
[4.58902, 4.95833, 1.50352, 0.10036],
[4.51242, 4.82226, 1.49972, 0.10412],
[4.4482, 4.6727, 1.49972, 0.10853],
[4.39752, 4.50966, 1.49972, 0.11384],
[4.3615, 4.33339, 1.49972, 0.11997],
[4.34139, 4.1442, 1.49972, 0.12686],
[4.33825, 3.94282, 1.49972, 0.1343],
[4.35267, 3.73044, 1.49972, 0.14194],
[4.38446, 3.50878, 1.49972, 0.14931],
[4.43253, 3.27985, 1.49972, 0.15597],
[4.49467, 3.04577, 1.49972, 0.16149],
[4.56674, 2.81179, 1.49972, 0.16325],
[4.62082, 2.59208, 1.49972, 0.15088],
[4.65612, 2.38832, 1.49972, 0.13789],
[4.67358, 2.2003, 1.49972, 0.12591],
[4.67489, 2.02678, 1.49972, 0.11571],
[4.66172, 1.86636, 1.49972, 0.10733],
[4.63553, 1.71771, 1.49972, 0.10064],
[4.59749, 1.57973, 1.49972, 0.09543],
[4.54854, 1.45149, 1.49972, 0.09153],
[4.48943, 1.33221, 1.49972, 0.08876],
[4.42067, 1.22134, 1.49972, 0.08699],
[4.34259, 1.11846, 1.50819, 0.08563],
[4.2554, 1.0233, 1.52437, 0.08467],
[4.15909, 0.9357, 1.553, 0.08383],
[4.0536, 0.85561, 1.59623, 0.08298],
[3.93876, 0.78304, 1.64538, 0.08257],
[3.81422, 0.71814, 1.71379, 0.08194],
[3.67963, 0.66111, 1.79291, 0.08153],
[3.53452, 0.61222, 1.89039, 0.081],
[3.37845, 0.57183, 2.00119, 0.08056],
[3.21101, 0.54036, 2.14499, 0.07943],
[3.03233, 0.51814, 2.31992, 0.07761],
[2.84362, 0.50533, 2.53576, 0.07459],
[2.64875, 0.5016, 2.8199, 0.06912],
[2.44864, 0.50587, 3.21683, 0.06222],
[2.24567, 0.51666, 3.02822, 0.06712],
[2.04253, 0.53378, 2.81904, 0.07232],
[1.83993, 0.55698, 2.66, 0.07666],
[1.63808, 0.58606, 2.53442, 0.08047],
[1.43701, 0.62086, 2.44439, 0.08348],
[1.23665, 0.66122, 2.38321, 0.08576],
[1.03691, 0.70701, 2.34074, 0.08754],
[0.83767, 0.75804, 2.327, 0.08839],
[0.63881, 0.81412, 2.32627, 0.08882],
[0.4402, 0.87502, 2.32627, 0.0893],
[0.24174, 0.94045, 2.32627, 0.08983],
[0.04334, 1.01013, 2.32627, 0.09039],
[-0.15507, 1.08374, 2.32627, 0.09097],
[-0.35357, 1.16093, 2.32627, 0.09155],
[-0.55219, 1.24137, 2.32627, 0.09212],
[-0.75096, 1.32472, 2.32627, 0.09265],
[-0.94992, 1.41061, 2.32627, 0.09316],
[-1.14632, 1.49266, 2.32627, 0.0915],
[-1.34129, 1.56993, 2.30873, 0.09084],
[-1.53444, 1.64111, 2.30873, 0.08916],
[-1.72538, 1.70495, 2.30873, 0.0872],
[-1.91385, 1.76064, 2.30873, 0.08513],
[-2.09969, 1.8076, 2.30873, 0.08302],
[-2.28278, 1.84546, 2.30873, 0.08098],
[-2.46306, 1.874, 2.30873, 0.07906],
[-2.64053, 1.89321, 2.30873, 0.07732],
[-2.81525, 1.90319, 2.30873, 0.0758],
[-2.98727, 1.90413, 2.30873, 0.07451],
[-3.15672, 1.89634, 2.30873, 0.07347],
[-3.32367, 1.88013, 2.07627, 0.08079],
[-3.48826, 1.85599, 1.90706, 0.08723],
[-3.65063, 1.82442, 1.79841, 0.09197],
[-3.81089, 1.78599, 1.73173, 0.09517],
[-3.96918, 1.74131, 1.68996, 0.09732],
[-4.12565, 1.6911, 1.68178, 0.09771],
[-4.27022, 1.63973, 1.68178, 0.09123],
[-4.41557, 1.59403, 1.68178, 0.09059],
[-4.56189, 1.55464, 1.68178, 0.0901],
[-4.70936, 1.52188, 1.68178, 0.08982],
[-4.8581, 1.49598, 1.68178, 0.08977],
[-5.00818, 1.47686, 1.68178, 0.08996],
[-5.15961, 1.46434, 1.68178, 0.09035],
[-5.31235, 1.45799, 1.68178, 0.0909],
[-5.46631, 1.45726, 1.68178, 0.09155],
[-5.62136, 1.46143, 1.68178, 0.09222],
[-5.77731, 1.46964, 1.68178, 0.09286],
[-5.93397, 1.48101, 1.68178, 0.0934],
[-6.07945, 1.4936, 1.68178, 0.08683],
[-6.22375, 1.50189, 1.68178, 0.08594],
[-6.36637, 1.50402, 1.68178, 0.08481],
[-6.50696, 1.49859, 1.68178, 0.08366],
[-6.64526, 1.48453, 1.68178, 0.08266],
[-6.7811, 1.46106, 1.68178, 0.08197],
[-6.9144, 1.42761, 1.68178, 0.08172],
[-7.04507, 1.38366, 1.68178, 0.08198],
[-7.17311, 1.32887, 1.68509, 0.08265],
[-7.29849, 1.2628, 1.71273, 0.08275],
[-7.42122, 1.18506, 1.75232, 0.08291],
[-7.54128, 1.09509, 1.82018, 0.08243],
[-7.65871, 0.99243, 1.90019, 0.08208],
[-7.77354, 0.87645, 2.00102, 0.08157],
[-7.88584, 0.74637, 2.13599, 0.08045],
[-7.99576, 0.60148, 2.285, 0.07959],
[-8.10355, 0.44094, 2.285, 0.08463],
[-8.20968, 0.26399, 2.285, 0.0903],
[-8.31493, 0.06971, 2.285, 0.0967],
[-8.4208, -0.14346, 2.285, 0.10416],
[-8.52355, -0.36439, 2.285, 0.10663],
[-8.61702, -0.58188, 2.285, 0.1036],
[-8.70012, -0.79532, 2.285, 0.10024],
[-8.7722, -1.00421, 2.285, 0.09671],
[-8.83291, -1.20823, 2.285, 0.09315],
[-8.88214, -1.40717, 2.285, 0.08969],
[-8.92011, -1.60105, 2.285, 0.08646],
[-8.94716, -1.78998, 2.285, 0.08353],
[-8.96368, -1.97414, 2.285, 0.08092],
[-8.97015, -2.15382, 2.285, 0.07869],
[-8.96704, -2.32935, 2.285, 0.07683],
[-8.95476, -2.50107, 2.21525, 0.07771],
[-8.93365, -2.66935, 1.99731, 0.08492],
[-8.90407, -2.83461, 1.83138, 0.09167],
[-8.8663, -2.9973, 1.69965, 0.09827],
[-8.82064, -3.15791, 1.59491, 0.10469],
[-8.76726, -3.31693, 1.51013, 0.11108],
[-8.70625, -3.47492, 1.44816, 0.11695],
[-8.63762, -3.63246, 1.39162, 0.12348],
[-8.56132, -3.79022, 1.3545, 0.12938],
[-8.47721, -3.9489, 1.3209, 0.13596],
[-8.38511, -4.10915, 1.30634, 0.14149],
[-8.28513, -4.27125, 1.3, 0.1465],
[-8.17856, -4.43377, 1.3, 0.1495],
[-8.07066, -4.5901, 1.3, 0.14612],
[-7.96538, -4.73656, 1.3, 0.13875],
[-7.86039, -4.87816, 1.3, 0.13559],
[-7.75483, -5.01542, 1.3, 0.1332],
[-7.64782, -5.14841, 1.3, 0.1313],
[-7.5383, -5.27736, 1.3, 0.13015],
[-7.42495, -5.40268, 1.3, 0.12998],
[-7.30455, -5.52473, 1.3, 0.13188],
[-7.17066, -5.64546, 1.3, 0.13867],
[-7.01605, -5.76473, 1.3, 0.15021],
[-6.84348, -5.87294, 1.3, 0.15668],
[-6.66849, -5.95699, 1.3, 0.14933],
[-6.50055, -6.01428, 1.3, 0.1365],
[-6.34267, -6.04753, 1.3, 0.12411],
[-6.19508, -6.06045, 1.3, 0.11397],
[-6.0573, -6.05588, 1.3, 0.10604],
[-5.92866, -6.03614, 1.3, 0.10011],
[-5.80868, -6.00278, 1.3, 0.0958],
[-5.69688, -5.95703, 1.3, 0.09292],
[-5.59299, -5.89974, 1.3035, 0.09101],
[-5.49686, -5.83148, 1.31517, 0.08965],
[-5.40846, -5.75256, 1.33843, 0.08854],
[-5.32791, -5.66312, 1.37141, 0.08777],
[-5.2554, -5.56317, 1.4093, 0.08762],
[-5.19135, -5.45242, 1.44893, 0.0883],
[-5.13621, -5.33056, 1.44893, 0.09231],
[-5.0906, -5.1971, 1.44893, 0.09734],
[-5.05522, -5.05144, 1.44893, 0.10345],
[-5.03081, -4.89298, 1.44893, 0.11066],
[-5.01817, -4.72103, 1.44893, 0.11899],
[-5.01792, -4.53509, 1.44893, 0.12833],
[-5.03029, -4.33497, 1.44893, 0.13838],
[-5.05475, -4.12128, 1.44893, 0.14845],
[-5.09252, -3.87981, 1.44893, 0.16868],
[-5.11499, -3.64293, 1.44893, 0.16422],
[-5.11943, -3.4168, 1.44893, 0.1561],
[-5.10545, -3.20612, 1.44893, 0.14572],
[-5.07442, -3.01302, 1.44893, 0.13499],
[-5.02831, -2.83774, 1.44893, 0.12508],
[-4.96903, -2.67962, 1.44893, 0.11655],
[-4.89824, -2.53762, 1.44893, 0.10951],
[-4.81721, -2.41073, 1.44893, 0.1039],
[-4.72698, -2.298, 1.44893, 0.09966],
[-4.62833, -2.19862, 1.44893, 0.09664],
[-4.52176, -2.11208, 1.44893, 0.09475],
[-4.40765, -2.03798, 1.45379, 0.09359],
[-4.28619, -1.97616, 1.47298, 0.09252],
[-4.1575, -1.92656, 1.49243, 0.09241],
[-4.02146, -1.88953, 1.52597, 0.09239],
[-3.87789, -1.86555, 1.57415, 0.09247],
[-3.72657, -1.8553, 1.62974, 0.09306],
[-3.5672, -1.85973, 1.70178, 0.09369],
[-3.39956, -1.87997, 1.79057, 0.0943],
[-3.22371, -1.91723, 1.83835, 0.09778],
[-3.04015, -1.97274, 1.81154, 0.10586],
[-2.85043, -2.04698, 1.79506, 0.1135],
[-2.65754, -2.13902, 1.79017, 0.11939],
[-2.46565, -2.24587, 1.7844, 0.12308],
[-2.27878, -2.36314, 1.7844, 0.12364],
[-2.09887, -2.48645, 1.7844, 0.12223],
[-1.92528, -2.61283, 1.7844, 0.12034],
[-1.75583, -2.74071, 1.7844, 0.11897],
[-1.59368, -2.85977, 1.7844, 0.11274],
[-1.43313, -2.97249, 1.77549, 0.11049],
[-1.27329, -3.07794, 1.73987, 0.11006],
[-1.11331, -3.17533, 1.71791, 0.10902],
[-0.95252, -3.26392, 1.70274, 0.10782],
[-0.79044, -3.34299, 1.6921, 0.10657],
[-0.62683, -3.41179, 1.6921, 0.1049],
[-0.46162, -3.46964, 1.6921, 0.10345],
[-0.29497, -3.51584, 1.6921, 0.1022],
[-0.1272, -3.54977, 1.6921, 0.10116],
[0.04119, -3.5708, 1.6921, 0.10029],
[0.20956, -3.57852, 1.6921, 0.09961],
[0.37716, -3.5726, 1.6921, 0.09911],
[0.54315, -3.55285, 1.6921, 0.09879],
[0.7067, -3.51919, 1.6921, 0.09868],
[0.86698, -3.47172, 1.6921, 0.09879],
[1.02318, -3.41047, 1.6921, 0.09916],
[1.17457, -3.33557, 1.6921, 0.09982],
[1.32047, -3.24702, 1.6921, 0.10086],
[1.46024, -3.1447, 1.6921, 0.10237],
[1.59331, -3.02821, 1.6921, 0.10452],
[1.72384, -2.89123, 1.6921, 0.11182],
[1.8599, -2.77334, 1.6921, 0.10639],
[2.00074, -2.67301, 1.6921, 0.10219],
[2.14561, -2.58911, 1.6921, 0.09894],
[2.29375, -2.5208, 1.6921, 0.09641],
[2.44443, -2.46748, 1.69847, 0.09411],
[2.59692, -2.42847, 1.712, 0.09194],
[2.75053, -2.40315, 1.73356, 0.08981],
[2.90465, -2.39091, 1.77118, 0.08729],
[3.05876, -2.39106, 1.82298, 0.08454],
[3.21245, -2.40285, 1.87924, 0.08202],
[3.36541, -2.4255, 1.82477, 0.08474],
[3.51746, -2.45826, 1.777, 0.08753],
[3.66853, -2.50027, 1.74007, 0.09011],
[3.81867, -2.55072, 1.71327, 0.09245],
[3.96811, -2.60877, 1.69826, 0.0944],
[4.11746, -2.67368, 1.69001, 0.09636],
[4.26811, -2.74498, 1.69001, 0.09862],
[4.42239, -2.8227, 1.69001, 0.10222],
[4.5827, -2.90681, 1.69001, 0.10712],
[4.7544, -2.9951, 1.69001, 0.11424],
[4.92695, -3.08011, 1.69001, 0.11382],
[5.10079, -3.16034, 1.69001, 0.11329],
[5.27644, -3.23442, 1.69001, 0.1128],
[5.45452, -3.30105, 1.69001, 0.11251],
[5.63587, -3.35902, 1.69001, 0.11265],
[5.82161, -3.4071, 1.69001, 0.11353],
[6.0131, -3.44383, 1.69001, 0.11537],
[6.21106, -3.46709, 1.69001, 0.11794],
[6.41319, -3.4745, 1.69001, 0.11968],
[6.61237, -3.4645, 1.69001, 0.118],
[6.80045, -3.43798, 1.69001, 0.11239],
[6.97389, -3.39734, 1.69001, 0.10541],
[7.13285, -3.34478, 1.69001, 0.09907],
[7.27886, -3.2818, 1.69001, 0.09409],
[7.41355, -3.20929, 1.69001, 0.09051],
[7.53827, -3.12772, 1.69001, 0.08818],
[7.65396, -3.03726, 1.69174, 0.08682],
[7.7613, -2.93784, 1.70351, 0.08588],
[7.86067, -2.82928, 1.72587, 0.08527],
[7.95226, -2.71129, 1.75871, 0.08493],
[8.03608, -2.58349, 1.8016, 0.08483],
[8.11194, -2.44546, 1.85487, 0.08491],
[8.17953, -2.29674, 1.92155, 0.08502],
[8.2384, -2.13689, 1.99529, 0.08537],
[8.28796, -1.9655, 2.08629, 0.08551],
[8.32757, -1.78236, 2.19668, 0.0853],
[8.35663, -1.58754, 2.32837, 0.0846],
[8.37468, -1.38149, 2.49014, 0.08306],
[8.38156, -1.16515, 2.69484, 0.08032],
[8.37754, -0.93994, 2.92397, 0.07703],
[8.36341, -0.70762, 2.76559, 0.08416],
[8.34047, -0.4701, 2.62761, 0.09081],
[8.31052, -0.2292, 2.50595, 0.09687],
[8.27566, 0.01361, 2.39208, 0.10255],
[8.23813, 0.25723, 2.28845, 0.10771],
[8.20019, 0.50099, 2.19361, 0.11246],
[8.16226, 0.74474, 2.0753, 0.11887]]

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
