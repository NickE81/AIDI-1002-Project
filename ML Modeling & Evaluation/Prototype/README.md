Make sure a conda environment is running on your system

### Modes
To train a new model, put train() in line 53
To load a pre-trained model, put load() in line 53

### How to run?
1. run pip install -r requirements.txt
2. run python QLearning.py
Note: You will get an error saying "TypeError: render() got an unexpected keyword argument 'mode' "
3. Go to the location where the error was found, and remove "mode='human' " from self.env.render(mode='human')
4. Run again and it will work