import base64
import io
import os
import pathlib
import sys

import pandas as pd
from flask import Flask, render_template, request, send_from_directory, url_for
from matplotlib.figure import Figure

# Add parent directory to path to import custom modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from model.util.data_path import cassava_price_avg, corn_price_avg
from utils.balance_price_calculation import price_ratio

app = Flask(
    __name__,
    static_folder=os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
        "static",
    ),
    template_folder=os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
        "templates",
    ),
)

# Set the project root path
project_root = pathlib.Path(__file__).parent.parent.parent.absolute()
model_images_path = project_root / "src" / "model" / "image"


def load_data(file_path):
    """Load data from CSV file"""
    try:
        return pd.read_csv(file_path)
    except Exception as e:
        print(f"Error loading data from {file_path}: {e}")
        return pd.DataFrame()


def generate_price_chart(data, title="Price Trend", x_label="Date", y_label="Price"):
    """Generate a matplotlib chart and return as base64 encoded string"""
    fig = Figure(figsize=(10, 6))
    ax = fig.add_subplot(1, 1, 1)

    if "date" in data.columns and "price" in data.columns:
        ax.plot(data["date"], data["price"])
        ax.set_title(title)
        ax.set_xlabel(x_label)
        ax.set_ylabel(y_label)
        fig.tight_layout()

        # Save plot to a bytes buffer
        buf = io.BytesIO()
        fig.savefig(buf, format="png")
        buf.seek(0)

        # Encode the bytes as base64 string
        data_uri = base64.b64encode(buf.read()).decode("utf-8")
        return f"data:image/png;base64,{data_uri}"
    return None


@app.route("/")
def index():
    """Landing page route"""
    return render_template("index.html", title="AI Crop Land-Used Analysis")


@app.route("/data")
def data_overview():
    """Data overview page"""
    cassava_data = load_data(cassava_price_avg)
    corn_data = load_data(corn_price_avg)

    return render_template(
        "data.html",
        title="Crop Price Data Overview",
        cassava_data=cassava_data.head(10).to_html(classes="table table-striped"),
        corn_data=corn_data.head(10).to_html(classes="table table-striped"),
    )


@app.route("/visualization")
def visualization():
    """Data visualization page"""
    cassava_data = load_data(cassava_price_avg)
    corn_data = load_data(corn_price_avg)

    cassava_chart = generate_price_chart(cassava_data, title="Cassava Price Trend")
    corn_chart = generate_price_chart(corn_data, title="Corn Price Trend")

    return render_template(
        "visualization.html",
        title="Crop Price Visualization",
        cassava_chart=cassava_chart,
        corn_chart=corn_chart,
    )


@app.route("/forecast")
def forecast():
    """Forecast results page"""
    # Use the pre-generated forecast images
    cassava_forecast_img = url_for(
        "static", filename="images/cassava_prices_forecast.png"
    )
    corn_forecast_img = url_for("static", filename="images/corn_prices_forecast.png")

    return render_template(
        "forecast.html",
        title="Crop Price Forecasts",
        cassava_forecast=cassava_forecast_img,
        corn_forecast=corn_forecast_img,
    )


@app.route("/calculator", methods=["GET", "POST"])
def calculator():
    """Price ratio calculator page"""
    result = None
    if request.method == "POST":
        try:
            prices = {
                "cassava": float(request.form.get("cassava", 0)),
                "corn": float(request.form.get("corn", 0)),
                "soybean": float(request.form.get("soybean", 0)),
                "green_beans": float(request.form.get("green_beans", 0)),
            }
            result = price_ratio(prices)
        except Exception as e:
            result = {"error": str(e)}

    return render_template(
        "calculator.html", title="Price Ratio Calculator", result=result
    )


@app.route("/about")
def about():
    """About page"""
    return render_template("about.html", title="About This Project")


@app.route("/images/<path:filename>")
def serve_model_images(filename):
    """Serve model images directly from the model/image directory"""
    return send_from_directory(model_images_path, filename)


if __name__ == "__main__":
    # Create directories for templates and static files if they don't exist
    os.makedirs(os.path.join(project_root, "templates"), exist_ok=True)
    os.makedirs(os.path.join(project_root, "static", "css"), exist_ok=True)
    os.makedirs(os.path.join(project_root, "static", "js"), exist_ok=True)
    os.makedirs(os.path.join(project_root, "static", "images"), exist_ok=True)

    # Copy forecast images to static folder
    import shutil

    for image_file in ["cassava_prices_forecast.png", "corn_prices_forecast.png"]:
        source = model_images_path / image_file
        destination = project_root / "static" / "images" / image_file
        if source.exists():
            shutil.copy(str(source), str(destination))

    app.run(debug=True, port=5000)
