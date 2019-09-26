# Solving captcha on projecteuler.com with multiclass image classification

## setup
```
git clone 
cd 
virtualenv -p /usr/local/bin/python3 venv
source venv/bin/activate
pip install -r requirements.txt
```

### step 1: Extract letters from images
```
python extract_single_letters_from_captchas.py
```

### Train Keras model, and run
```
python train_model.py
python solve_captchas_with_model.py

```

### Train XGBoost model
```
python train_model.py
```

## todo
* refactor
* serve models from python api
* firefox/chrome extension that calls api