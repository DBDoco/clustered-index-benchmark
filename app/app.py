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
    durations_with_index_read = []
    data_counts_with_index_read = []
    durations_without_index_read = []
    data_counts_without_index_read = []

    durations_with_index_write = []
    data_counts_with_index_write = []
    durations_without_index_write = []
    data_counts_without_index_write = []

    # Define a route for reading data with a clustered index
    @app.route('/read_with_index')
    def read_with_index():
        nonlocal durations_with_index_read, data_counts_with_index_read

        # Record the start time for measuring duration
        start_time = time.time() * 1000

        # Query data items with a fake UUID and measure duration
        data_items = DataItem.query.filter_by(key=fake.uuid4()).all()

        # Record the end time and calculate duration
        end_time = time.time() * 1000
        duration = end_time - start_time

        # Store duration and data count
        durations_with_index_read.append(duration)
        data_counts_with_index_read.append(len(data_items))

        # Return JSON response with result, duration, and data count
        return jsonify({
            "result": "Read with index complete",
            "duration": duration,
            "data_count": len(data_items),
        })

    # Define a route for reading data without a clustered index
    @app.route('/read_without_index')
    def read_without_index():
        nonlocal durations_without_index_read, data_counts_without_index_read

        # Record the start time for measuring duration
        start_time = time.time() * 1000

        # Query data items from the database with a fake text and measure duration
        data_items = DataItem.query.filter_by(value=fake.text()).all()

        # Record the end time and calculate duration
        end_time = time.time() * 1000
        duration = end_time - start_time

        # Store duration and data count
        durations_without_index_read.append(duration)
        data_counts_without_index_read.append(len(data_items))

        # Return JSON response with result, duration, and data count
        return jsonify({
            "result": "Read without index complete",
            "duration": duration,
            "data_count": len(data_items),
        })
    
    @app.route('/write_with_index')
    def write_with_index():
        nonlocal durations_with_index_write, data_counts_with_index_write

        # Record the start time for measuring duration
        start_time = time.time() * 1000

        # Add fake data items to the database with a fake UUID for testing
        fake_data_items = []
        for _ in range(100):
            key = fake.uuid4()
            data_item = DataItem(key=key, value=fake.text())
            db.session.add(data_item)
            fake_data_items.append({"key": data_item.key, "value": data_item.value})

        # Commit the changes to the database
        db.session.commit()

        # Record the end time and calculate duration
        end_time = time.time() * 1000
        duration = end_time - start_time

        # Store duration and data count
        durations_with_index_write.append(duration)
        data_counts_with_index_write.append(len(fake_data_items))

        # Return JSON response with result, duration, and data count
        return jsonify({
            "result": "Write with index complete",
            "duration": duration,
            "data_count": len(fake_data_items),
        })

    # Define a route for writing data without a clustered index
    @app.route('/write_without_index')
    def write_without_index():
        nonlocal durations_without_index_write, data_counts_without_index_write

        # Record the start time for measuring duration
        start_time = time.time() * 1000

        # Add fake data items to the database with a fake UUID for testing
        fake_data_items = []
        for _ in range(100):
            key = fake.uuid4()
            data_item = DataItem(key=key, value=fake.text())
            db.session.add(data_item)
            fake_data_items.append({"key": data_item.key, "value": data_item.value})

        # Commit the changes to the database
        db.session.commit()

        # Record the end time and calculate duration
        end_time = time.time() * 1000
        duration = end_time - start_time

        # Store duration and data count
        durations_without_index_write.append(duration)
        data_counts_without_index_write.append(len(fake_data_items))

        # Return JSON response with result, duration, and data count
        return jsonify({
            "result": "Write without index complete",
            "duration": duration,
            "data_count": len(fake_data_items),
        })

    # Define a route for generating and serving a performance comparison plot
    @app.route('/get_plot')
    def get_plot():
        nonlocal durations_with_index_read, durations_without_index_read, durations_with_index_write, durations_without_index_write

        # Calculate average and median durations for read scenarios
        avg_with_index_read = np.mean(durations_with_index_read)
        median_with_index_read = np.median(durations_with_index_read)
        avg_without_index_read = np.mean(durations_without_index_read)
        median_without_index_read = np.median(durations_without_index_read)

        # Calculate average and median durations for write scenarios
        avg_with_index_write = np.mean(durations_with_index_write)
        median_with_index_write = np.median(durations_with_index_write)
        avg_without_index_write = np.mean(durations_without_index_write)
        median_without_index_write = np.median(durations_without_index_write)

        # Create a static folder for storing generated plots
        static_folder = os.path.join(os.getcwd(), 'static')
        os.makedirs(static_folder, exist_ok=True)

        # Create a bar plot for total, average, and median durations for reads
        plt.figure(figsize=(15, 10))

        plt.subplot(2, 3, 1)
        plt.bar(['With Index', 'Without Index'], [sum(durations_with_index_read), sum(durations_without_index_read)])
        plt.title('Total Duration Comparison (Read)')
        plt.ylabel('Total Duration (ms)')

        plt.subplot(2, 3, 2)
        plt.bar(['With Index', 'Without Index'], [avg_with_index_read, avg_without_index_read])
        plt.title('Average Duration Comparison (Read)')
        plt.ylabel('Average Duration (ms)')

        plt.subplot(2, 3, 3)
        plt.bar(['With Index', 'Without Index'], [median_with_index_read, median_without_index_read])
        plt.title('Median Duration Comparison (Read)')
        plt.ylabel('Median Duration (ms)')

        # Create a bar plot for total, average, and median durations for writes
        plt.subplot(2, 3, 4)
        plt.bar(['With Index', 'Without Index'], [sum(durations_with_index_write), sum(durations_without_index_write)])
        plt.title('Total Duration Comparison (Write)')
        plt.ylabel('Total Duration (ms)')

        plt.subplot(2, 3, 5)
        plt.bar(['With Index', 'Without Index'], [avg_with_index_write, avg_without_index_write])
        plt.title('Average Duration Comparison (Write)')
        plt.ylabel('Average Duration (ms)')

        plt.subplot(2, 3, 6)
        plt.bar(['With Index', 'Without Index'], [median_with_index_write, median_without_index_write])
        plt.title('Median Duration Comparison (Write)')
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
        nonlocal durations_with_index_read, durations_without_index_read, durations_with_index_write, durations_without_index_write

        # Clear stored durations for both scenarios
        durations_with_index_read.clear()
        durations_without_index_read.clear()
        durations_with_index_write.clear()
        durations_without_index_write.clear()

        # Clear the database
        with app.app_context():
            db.drop_all()
            db.create_all()

        # Return JSON response indicating that durations and database are cleared
        return jsonify({"result": "Durations and database cleared"})

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
