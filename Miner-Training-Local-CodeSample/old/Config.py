MODEL_PATH = "TrainedModels_test/"
LOG_PATH  = "Data_test/data_"


N_EPISODE = 10000 #The number of episodes for training
MAX_STEP = 100   #The number of steps for each episode
BATCH_SIZE = 32   #The number of experiences for each replay
MEMORY_SIZE = 100000 #The size of the batch for storing experiences
SAVE_NETWORK = 100  # After this number of episodes, the DQN model is saved for testing later.
INITIAL_REPLAY_SIZE = 1000 #The number of experiences are stored in the memory batch before starting replaying
INPUTNUM = 207 #The number of input values for the DQN model
ACTIONNUM = 6  #The number of actions output from the DQN model
MAP_MAX_X = 21 #Width of the Map
MAP_MAX_Y = 9  #Height of the Map
DEBUG = False



# # Parameters for training a DQN model
# N_EPISODE = 10000000 #The number of episodes for training
# MAX_STEP = 100   #The number of steps for each episode
# BATCH_SIZE = 32   #The number of experiences for each replay 
# MEMORY_SIZE = 100000 #The size of the batch for storing experiences
# SAVE_NETWORK = 100  # After this number of episodes, the DQN model is saved for testing later. 
# INITIAL_REPLAY_SIZE = 40  #The number of experiences are stored in the memory batch before starting replaying
# INPUTNUM = 198 + 6 #The number of input values for the DQN model
# ACTIONNUM = 6  #The number of actions output from the DQN model
# MAP_MAX_X = 21 #Width of the Map
# MAP_MAX_Y = 9  #Height of the Map