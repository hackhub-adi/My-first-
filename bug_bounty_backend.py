import os
from flask import Flask, request, jsonify
import firebase_admin
from firebase_admin import credentials, firestore

app = Flask(__name__)

# Initialize Firebase Admin SDK
# Note: In a real application, you should handle the credentials securely.
# For this demo, we'll initialize it if the env var GOOGLE_APPLICATION_CREDENTIALS is set,
# or we'll mock the database if it's not set so the app can still run for testing.

db = None
try:
    if not firebase_admin._apps:
        # This will use the default credentials (e.g. from GOOGLE_APPLICATION_CREDENTIALS)
        cred = credentials.ApplicationDefault()
        firebase_admin.initialize_app(cred)
    db = firestore.client()
except Exception as e:
    print(f"Warning: Could not initialize Firebase Admin SDK. {e}")
    print("Using an in-memory mock database instead.")

    # Mock database for testing when Firebase credentials are not available
    class MockDB:
        def __init__(self):
            self.collections = {}

        def collection(self, name):
            if name not in self.collections:
                self.collections[name] = MockCollection(name)
            return self.collections[name]

    class MockCollection:
        def __init__(self, name):
            self.name = name
            self.documents = {}
            import uuid
            self.uuid = uuid

        def add(self, data):
            doc_id = str(self.uuid.uuid4())
            self.documents[doc_id] = MockDocument(doc_id, data)
            return None, self.documents[doc_id]

        def stream(self):
            return list(self.documents.values())

        def where(self, field, op, value):
            return MockQuery(self, field, op, value)

    class MockDocument:
        def __init__(self, id, data):
            self.id = id
            self._data = data

        def to_dict(self):
            return self._data

    class MockQuery:
        def __init__(self, collection, field, op, value):
            self.collection = collection
            self.field = field
            self.op = op
            self.value = value

        def stream(self):
            results = []
            for doc in self.collection.documents.values():
                doc_data = doc.to_dict()
                if self.field in doc_data:
                    if self.op == '==' and doc_data[self.field] == self.value:
                        results.append(doc)
            return results

    db = MockDB()

@app.route('/targets', methods=['POST'])
def add_target():
    """Add a new target URL."""
    data = request.get_json()
    if not data or 'url' not in data:
        return jsonify({'error': 'Missing url field'}), 400

    target_data = {
        'url': data['url'],
        'description': data.get('description', ''),
        'status': 'active'
    }

    try:
        # Add a new document to the 'targets' collection
        update_time, target_ref = db.collection('targets').add(target_data)
        return jsonify({
            'message': 'Target added successfully',
            'id': target_ref.id,
            'target': target_data
        }), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/targets', methods=['GET'])
def get_targets():
    """Retrieve all target URLs."""
    try:
        targets = []
        targets_ref = db.collection('targets')
        docs = targets_ref.stream()

        for doc in docs:
            target = doc.to_dict()
            target['id'] = doc.id
            targets.append(target)

        return jsonify({'targets': targets}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/scans', methods=['POST'])
def add_scan_result():
    """Add a scan result for a specific target."""
    data = request.get_json()
    if not data or 'target_id' not in data or 'result' not in data:
        return jsonify({'error': 'Missing required fields (target_id, result)'}), 400

    scan_data = {
        'target_id': data['target_id'],
        'result': data['result'],
        'vulnerabilities_found': data.get('vulnerabilities_found', 0),
        'timestamp': data.get('timestamp', 'unknown') # In a real app, use server timestamp
    }

    try:
        # Add a new document to the 'scans' collection
        update_time, scan_ref = db.collection('scans').add(scan_data)
        return jsonify({
            'message': 'Scan result added successfully',
            'id': scan_ref.id,
            'scan': scan_data
        }), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/scans/<target_id>', methods=['GET'])
def get_scans(target_id):
    """Retrieve scan results for a specific target."""
    try:
        scans = []
        scans_ref = db.collection('scans')
        # Query for scans belonging to the target_id
        query = scans_ref.where('target_id', '==', target_id)
        docs = query.stream()

        for doc in docs:
            scan = doc.to_dict()
            scan['id'] = doc.id
            scans.append(scan)

        return jsonify({'target_id': target_id, 'scans': scans}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5001)
