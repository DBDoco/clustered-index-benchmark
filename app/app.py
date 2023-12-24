# Import necessary libraries and modules
from flask import Flask, jsonify, send_file
from faker import Faker
import time
import matplotlib.pyplot as plt
import os
from flask_sqlalchemy import SQLAlchemy
import numpy as np

# Define the path for storing the performance comparison plot in the container
IMAGE_PATH_IN_CONTAINER = '/app/static/performance_comparison.png'

# Initialize Faker for generating fake data
fake = Faker()

# Initialize SQLAlchemy for database operations
db = SQLAlchemy()

# Define a function to create the Flask application
def create_app():
    app = Flask(__name__)

    # Configure the SQLAlchemy database URI
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://user:password@db/experiment_db'

    # Initialize the database with the Flask app
    db.init_app(app)

    # Define the database model for storing data items
    class DataItem(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        key = db.Column(db.String(255), index=True, unique=True, nullable=False)
        value = db.Column(db.Text)

    # Create an index on the 'key' column for optimized queries
    db.Index('idx_key', DataItem.key)

    # Initialize lists to store durations and data counts for two scenarios
    durations_with_index = []
    data_counts_with_index = []
    durations_without_index = []
    data_counts_without_index = []

    # Define a route for reading data with a clustered index
    @app.route('/read_with_index')
    def read_with_index():
        nonlocal durations_with_index, data_counts_with_index

        # Record the start time for measuring duration
        start_time = time.time() * 1000

        # Query data items with a fake UUID and measure duration
        data_items = DataItem.query.filter_by(key=fake.uuid4()).all()

        # Record the end time and calculate duration
        end_time = time.time() * 1000
        duration = end_time - start_time

        # Store duration and data count
        durations_with_index.append(duration)
        data_counts_with_index.append(len(data_items))

        # Add fake data items to the database for testing
        fake_data_items = []
        for _ in range(100):
            key = fake.uuid4()
            data_item = DataItem(key=key, value=fake.text())
            db.session.add(data_item)
            fake_data_items.append({"key": data_item.key, "value": data_item.value})

        # Return JSON response with result, duration, and data count
        return jsonify({
            "result": "Read with index complete",
            "duration": duration,
            "data_count": len(fake_data_items),
        })

    # Define a route for reading data without a clustered index
    @app.route('/read_without_index')
    def read_without_index():
        nonlocal durations_without_index, data_counts_without_index

        # Record the start time for measuring duration
        start_time = time.time() * 1000

        # Query data items with a fake text and measure duration
        data_items = DataItem.query.filter_by(value=fake.text()).all()

        # Record the end time and calculate duration
        end_time = time.time() * 1000
        duration = end_time - start_time

        # Store duration and data count
        durations_without_index.append(duration)
        data_counts_without_index.append(len(data_items))

        # Add fake data items to the database for testing
        fake_data_items = []
        for _ in range(100):
            key = fake.uuid4()
            data_item = DataItem(key=key, value=fake.text())
            db.session.add(data_item)
            fake_data_items.append({"key": data_item.key, "value": data_item.value})

        # Return JSON response with result, duration, and data count
        return jsonify({
            "result": "Read without index complete",
            "duration": duration,
            "data_count": len(fake_data_items),
        })

    # Define a route for generating and serving a performance comparison plot
    @app.route('/get_plot')
    def get_plot():
        nonlocal durations_with_index, durations_without_index

        # Calculate average and median durations for both scenarios
        avg_with_index = np.mean(durations_with_index)
        median_with_index = np.median(durations_with_index)
        avg_without_index = np.mean(durations_without_index)
        median_without_index = np.median(durations_without_index)

        # Create a static folder for storing generated plots
        static_folder = os.path.join(os.getcwd(), 'static')
        os.makedirs(static_folder, exist_ok=True)

        # Create a bar plot for total, average, and median durations
        plt.figure(figsize=(15, 5))
        plt.subplot(1, 3, 1)
        plt.bar(['With Index', 'Without Index'], [sum(durations_with_index), sum(durations_without_index)])
        plt.title('Total Duration Comparison')
        plt.ylabel('Total Duration (ms)')

        plt.subplot(1, 3, 2)
        plt.bar(['With Index', 'Without Index'], [avg_with_index, avg_without_index])
        plt.title('Average Duration Comparison')
        plt.ylabel('Average Duration (ms)')

        plt.subplot(1, 3, 3)
        plt.bar(['With Index', 'Without Index'], [median_with_index, median_without_index])
        plt.title('Median Duration Comparison')
        plt.ylabel('Median Duration (ms)')

        plt.tight_layout()

        # Save the combined plot image
        combined_path = '/app/static/duration_comparison_combined.png'
        plt.savefig(combined_path)
        plt.close()

        # Serve the saved plot as an attachment
        return send_file(combined_path, mimetype='image/png', as_attachment=True)

    # Define a route for clearing stored durations
    @app.route('/clear')
    def clear_durations():
        nonlocal durations_with_index, durations_without_index

        # Clear stored durations for both scenarios
        durations_with_index.clear()
        durations_without_index.clear()

        # Return JSON response indicating that durations are cleared
        return jsonify({"result": "Durations cleared"})

    # Return the Flask app instance
    return app

# Define a function for simulating data processing
def process_data():
    time.sleep(0.1)
    return "Data processing complete"

# Run the Flask app if the script is executed
if __name__ == '__main__':
    app = create_app()

    # Create the database tables within the Flask app context
    with app.app_context():
        db.create_all()

    # Run the Flask app on specified host and port
    app.run(host='0.0.0.0', port=8001)
