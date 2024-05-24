import threading
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
import signal
import boto3
from botocore.exceptions import ClientError, NoCredentialsError
import json

# Create a Flask app
app = Flask(__name__)

def handle_signal(sig, frame):
    print(f"Signal received: {sig}")
    app.logger.info(f"Signal received: {sig}")

def get_secret(secret_name, region_name="us-east-1"):
    # Create a Secrets Manager client
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )

    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
    except ClientError as e:
        raise e
    except NoCredentialsError as e:
        raise e

    # Parse the secret value as JSON
    secret_dict = json.loads(get_secret_value_response['SecretString'])

    return secret_dict

try:
    # Retrieve the secret value
    # secret = get_secret(secret_name="rds!db-eba76f1a-75ee-4617-bc0e-3fac8bcf8e53")
    # app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql://{secret['username']}:{secret['password']}"
    secret = get_secret(secret_name="dev/cpmi/MySql")
    app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql://{secret['username']}:{secret['password']}@{secret['host']}:{secret['port']}/{secret['dbInstanceIdentifier']}"

    # Start a new thread to handle signals
    signal_thread = threading.Thread(target=handle_signal, args=(signal.SIGINT, None))
    signal_thread.start()

    # Run the Flask app
    app.run(debug=True)
except NoCredentialsError as e:
    print("No AWS credentials found. Please set your credentials using environment variables or a credentials file.")

# Configure the database connection
db = SQLAlchemy(app)

# Define the Application class
class Application(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    scoped_year = db.Column(db.Integer, nullable=False)
    product_owner = db.Column(db.String(255), nullable=False)

    def __repr__(self):
        return f"<Application {self.id}: {self.name}>"

# Create the database tables
with app.app_context():
    db.create_all()

# Add a new application
@app.route("/applications", methods=["POST"])
def add_application():
    try:
        data = request.get_json()
        new_application = Application(
            name=data["name"],
            scoped_year=data["scoped_year"],
            product_owner=data["product_owner"]
        )
        db.session.add(new_application)
        db.session.commit()
        return jsonify({"message": "Application added successfully!"}), 201
    except Exception as e:
        return jsonify({"error": f"Error retrieving applications: {e}"}), 500


# Get all applications
@app.route("/applications", methods=["GET"])
def get_applications():
    try:
        applications = Application.query.all()
        return jsonify([
            {
                "id": app.id,
                "name": app.name,
                "scoped_year": app.scoped_year,
                "product_owner": app.product_owner
            }
            for app in applications
        ]), 200
    except Exception as e:
        return jsonify({"error": f"Error retrieving applications: {e}"}), 500

# Update an application
@app.route("/applications/<int:application_id>", methods=["PUT"])
def update_application(application_id):
    try:
        application_to_update = Application.query.get(application_id)
        if application_to_update:
            data = request.get_json()
            application_to_update.name = data["name"]
            application_to_update.scoped_year = data["scoped_year"]
            application_to_update.product_owner = data["product_owner"]
            db.session.commit()
            return jsonify({"message": "Application updated successfully!"}), 200
        else:
            return jsonify({"error": "Application not found."}), 404
    except Exception as e:
        return jsonify({"error": f"Error updating application: {e}"}), 500

# Delete an application
@app.route("/applications/<int:application_id>", methods=["DELETE"])
def delete_application(application_id):
    try:
        application_to_delete = Application.query.get(application_id)
        if application_to_delete:
            db.session.delete(application_to_delete)
            db.session.commit()
            return jsonify({"message": "Application deleted successfully!"}), 200
        else:
            return jsonify({"error": "Application not found."}), 404
    except Exception as e:
        return jsonify({"error": f"Error deleting application: {e}"}), 500

# Run the Flask app
if __name__ == "__main__":
    app.run()