from itertools import combinations , permutations


def eda_cnn(state = None, kernel_size = (7, 3), stride = 1):
    width = 21
    height = 9

    max_complexity = 0
    max_number_point = 0
    all_complexity = 0
    for i in range(int((width - kernel_size[0]) / stride) + 1):
        for j in range(int((height - kernel_size[1])/stride) + 1):

            window_size = [(i*stride, j*stride), (kernel_size[0] + i*stride - 1, kernel_size[1] + j*stride - 1)]
            print(window_size)

            number_point = 0
            for cell in state.mapInfo.golds:
                if check_in_window(window_size, cell):
                    number_point += 1
                    
            complexity = check_complexity(number_point)
            
            all_complexity += complexity
            max_number_point = max(max_number_point, number_point)
            max_complexity = max(max_complexity, complexity)

    print('max_number_point: {}'.format(max_number_point))
    print('max_complexity: {}'.format(max_complexity))
    print('all_complexity: {}'.format(all_complexity))

def check_in_window(window_size, cell):
    if cell['posx'] >= window_size[0][0] \
        and cell['posx'] <= window_size[1][0] \
        and cell['posy'] >= window_size[0][1] \
        and cell['posy'] <= window_size[1][1] \
        and cell['amount'] >= 200:
        return True

    return False

def check_complexity(number_point, number_point_target = 4):
    return max(len(list(permutations(range(number_point), number_point_target))), 1)
