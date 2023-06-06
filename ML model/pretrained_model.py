import pickle

adaboost_model = pickle.load(open('trained_adaboost_model.pkl', 'rb'))
x = [[52.0,23.4,590.0,55.01,1,21]]
z = adaboost_model.predict(x)
print(f"the pred is {z}")