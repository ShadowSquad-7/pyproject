import subprocess

def run_background_scripts():
    subprocess.Popen(["python", "app/parcers/yf_parcer.py"])
    subprocess.Popen(["python", "app/parcers/updater_btc.py"])
    subprocess.Popen(["python", "app/parcers/multi_updater.py"])
    subprocess.Popen(["python", "app/plotly/dash.py"])


