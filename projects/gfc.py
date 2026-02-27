import matplotlib
matplotlib.use("TkAgg")
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split


class PowerPredictor:

    def __init__(self, path):
        try:
            if path.endswith(".csv"):
                self.df = pd.read_csv(path)
            else:
                self.df = pd.read_excel(path)
        except Exception as e:
            raise Exception(f"Error loading dataset: {e}")

        self.day_data = None
        self.current_day = None
        self.y_test = None
        self.y_pred = None


    def day(self, name):

        self.current_day = name
        df = self.df[self.df["Day_of_week"] == name].copy()

        if df.empty:
            raise Exception(f"No data for {name}")

        df = df.interpolate()

        df["Reactive"] = (
            df["Lagging_Current_Reactive.Power_kVarh"]
            - df["Leading_Current_Reactive_Power_kVarh"]
        )

        df["Apparent"] = df["Usage_kWh"] / df["Lagging_Current_Power_Factor"]
        df["Time"] = df["NSM"] / 3600

        df.dropna(inplace=True)
        self.day_data = df

    


       
    def predict(self):

        if self.day_data is None:
            raise Exception("Run day() first")

        X = self.day_data[["Reactive", "Apparent", "Time"]]
        y = self.day_data["Usage_kWh"]

        if len(X) < 5:
            raise Exception("Not enough data")

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )

        model = LinearRegression()
        model.fit(X_train, y_train)

        y_pred = model.predict(X_test)

        self.y_test = y_test
        self.y_pred = y_pred

        fig, ax = plt.subplots(figsize=(6,4))

        ax.scatter(X_test["Time"], y_test, label="Actual")
        ax.scatter(X_test["Time"], y_pred, label="Predicted")
        ax.set_xlabel("Time (hrs)")
        ax.set_ylabel("Power Usage")
        ax.set_title(f"Prediction — {self.current_day}")
        ax.legend()
        ax.grid(True)

        return fig
    def metrics(self):

        if self.y_pred is None:
            return None

        r2 = r2_score(self.y_test, self.y_pred)
        mae = mean_absolute_error(self.y_test, self.y_pred)
        rmse = np.sqrt(mean_squared_error(self.y_test, self.y_pred))

        return round(r2,4), round(mae,4), round(rmse,4)

    def get_stats(self, day_name, time):

        df = self.df[self.df['Day_of_week'] == day_name].copy()

        if df.empty:
            return None

        df["Reactive"] = df['Lagging_Current_Reactive.Power_kVarh'] - df['Leading_Current_Reactive_Power_kVarh']
        df["Apparent"] = df['Usage_kWh'] / df['Lagging_Current_Power_Factor']
        df["Time"] = df["NSM"] / 3600

        df.dropna(inplace=True)

        X = df[["Reactive", "Apparent", "Time"]]
        y = df["Usage_kWh"]

        model = LinearRegression()
        model.fit(X, y)

        reactive = df["Reactive"].mean()
        apparent = df["Apparent"].mean()

        sample = pd.DataFrame([[reactive, apparent, time]],
                              columns=["Reactive", "Apparent", "Time"])

        prediction = model.predict(sample)[0]
        return round(prediction, 3)



root = tk.Tk()
root.title("Power Prediction System")
root.geometry("650x750")

path_v = tk.StringVar()

def browse():
    file = filedialog.askopenfilename()
    path_v.set(file)

tk.Label(root, text="Dataset Path").pack()
tk.Entry(root, textvariable=path_v, width=60).pack()
tk.Button(root, text="Browse File", command=browse).pack(pady=10)

tk.Label(root, text="Select Day").pack()
day_var = tk.StringVar()

day_box = ttk.Combobox(root, textvariable=day_var)
day_box["values"] = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
day_box.pack()

tk.Label(root, text="Enter Time (hours)").pack()
time_var = tk.DoubleVar()
tk.Entry(root, textvariable=time_var).pack()

result_var = tk.StringVar()
tk.Label(root, textvariable=result_var, font=("Arial", 12, "bold")).pack(pady=10)

plot_frame = tk.Frame(root)
metrics_frame = tk.Frame(root)
metrics_frame.pack(pady=10)

r2_label = tk.Label(metrics_frame, text="R²: -", font=("Arial",12))
r2_label.pack()

mae_label = tk.Label(metrics_frame, text="MAE: -", font=("Arial",12))
mae_label.pack()

rmse_label = tk.Label(metrics_frame, text="RMSE: -", font=("Arial",12))
rmse_label.pack()
plot_frame.pack(fill="both", expand=True)


def run_prediction():

    path = path_v.get()
    day = day_var.get()
    time = time_var.get()

    if path == "" or day == "":
        messagebox.showerror("Error","Select file and day")
        return

    try:
        obj = PowerPredictor(path)
        obj.day(day)

        fig = obj.predict()

        prediction = obj.get_stats(day, time)

        if prediction is None:
            result_var.set("No data available")
        else:
            result_var.set(f"Predicted Power = {prediction} kWh")

        
        for widget in plot_frame.winfo_children():
            widget.destroy()

        canvas = FigureCanvasTkAgg(fig, master=plot_frame)
        metrics = obj.metrics()

        if metrics:
            r2, mae, rmse = metrics
            r2_label.config(text=f"R²: {r2}")
            mae_label.config(text=f"MAE: {mae}")
            rmse_label.config(text=f"RMSE: {rmse}")
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

    except Exception as e:
        messagebox.showerror("Error", str(e))


tk.Button(root, text="Predict Power", command=run_prediction).pack(pady=15)

root.mainloop()
     







        

    
    
        

        