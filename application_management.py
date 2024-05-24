import threading
import streamlit as st
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
import signal

# Create a Flask app
app = Flask(__name__)

# Configure the database connection
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///applications.db'
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

# Streamlit interface
@app.route("/")
def index():
    st.title("CPMI Application Management")

    # Add a new application
    with st.form("add_application"):
        name = st.text_input("Application Name")
        scoped_year = st.number_input("Scoped Year")
        product_owner = st.text_input("Product Owner")

        submitted = st.form_submit_button("Add Application")

        if submitted:
            try:
                new_application = Application(
                    name=name,
                    scoped_year=scoped_year,
                    product_owner=product_owner
                )
                db.session.add(new_application)
                db.session.commit()
                st.success("Application added successfully!")
            except Exception as e:
                st.error(f"Error adding application: {e}")

    # Display existing applications
    st.header("Existing Applications")
    try:
        applications = Application.query.all()
        st.table(
            [
                [app.id, app.name, app.scoped_year, app.product_owner]
                for app in applications
            ]
        )
    except Exception as e:
        st.error(f"Error retrieving applications: {e}")

    # Update an application
    application_id = st.number_input("Application ID to Update")
    if application_id:
        try:
            application_to_update = Application.query.get(application_id)
            if application_to_update:
                with st.form("update_application"):
                    name = st.text_input("Application Name", application_to_update.name)
                    scoped_year = st.number_input(
                        "Scoped Year", application_to_update.scoped_year
                    )
                    product_owner = st.text_input(
                        "Product Owner", application_to_update.product_owner
                    )
                    # ... (add input fields for other properties)
                    submitted = st.form_submit_button("Update Application")

                    if submitted:
                        application_to_update.name = name
                        application_to_update.scoped_year = scoped_year
                        application_to_update.product_owner = product_owner
                        # ... (update other properties)
                        db.session.commit()
                        st.success("Application updated successfully!")
            else:
                st.error("Application not found.")
        except Exception as e:
            st.error(f"Error updating application: {e}")

    # Delete an application
    application_id_to_delete = st.number_input("Application ID to Delete")
    if application_id_to_delete:
        try:
            application_to_delete = Application.query.get(application_id_to_delete)
            if application_to_delete:
                if st.button(f"Delete Application {application_id_to_delete}"):
                    db.session.delete(application_to_delete)
                    db.session.commit()
                    st.success("Application deleted successfully!")
            else:
                st.error("Application not found.")
        except Exception as e:
            st.error(f"Error deleting application: {e}")

    return st.__dict__

# Run the Flask app
if __name__ == "__main__":
    def handle_signal(sig, frame):
        print(f"Signal received: {sig}")
        app.logger.info(f"Signal received: {sig}")
        app.exit()

        with app.app_context():
            # Start a new thread to handle signals
            signal_thread = threading.Thread(target=handle_signal, args=(signal.SIGINT,))
            signal_thread.start()

            app.run(debug=True)
