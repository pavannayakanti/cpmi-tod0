from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://nayakanp:123456@localhost/cpmi-todo'
db = SQLAlchemy(app)

class Application(db.Model):
    __tablename__ = 'applications'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    scoped_year = db.Column(db.Integer, nullable=False)
    product_owner = db.Column(db.String(255), nullable=False)
    engineering_lead = db.Column(db.String(255), nullable=False)
    qa_lead = db.Column(db.String(255), nullable=False)
    operations_lead = db.Column(db.String(255), nullable=False)
    devops_architect = db.Column(db.String(255), nullable=False)
    cloud_architect = db.Column(db.String(255), nullable=False)

    def __repr__(self):
        return f'<Application {self.name}>'


# Create Application
@app.route("/applications", methods=["POST"])
def create_application():
    data = request.get_json()
    application = Application(**data)
    db.session.add(application)
    db.session.commit()
    return jsonify({"message": "Application created successfully"}), 201

# Read Applications
@app.route("/applications", methods=["GET"])
def get_applications():
    applications = Application.query.all()
    return jsonify({"applications": applications}), 200

# Read a Specific Application
@app.route("/applications/<int:id>", methods=["GET"])
def get_application(id):
    application = Application.query.get(id)
    if not application:
        return jsonify({"message": "Application not found"}), 404
    return jsonify({"application": application}), 200

# Update an Application
@app.route("/applications/<int:id>", methods=["PUT"])
def update_application(id):
    data = request.get_json()
    application = Application.query.get(id)
    if not application:
        return jsonify({"message": "Application not found"}), 404
    application.name = data.get("name")
    application.scoped_year = data.get("scoped_year")
    # Update other properties
    db.session.commit()
    return jsonify({"message": "Application updated successfully"}), 200

# Delete an Application
@app.route("/applications/<int:id>", methods=["DELETE"])
def delete_application(id):
    application = Application.query.get(id)
    if not application:
        return jsonify({"message": "Application not found"}), 404
    db.session.delete(application)
    db.session.commit()
    return jsonify({"message": "Application deleted successfully"}), 200

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
