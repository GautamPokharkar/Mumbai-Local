from flask import Flask, render_template, request, redirect, url_for, session, make_response
import pandas as pd
import networkx as nx

# Load the dataset
data = pd.read_csv('BOMLOCAL.csv', encoding='latin1')

# Initialize the graph
G = nx.MultiGraph()

for i in range(len(data) - 1):
    if data['Line'][i] == data['Line'][i + 1]:
        G.add_edge(
            data['Station'][i],
            data['Station'][i + 1],
            key=f"{data['Line'][i]}_{i}",
            line=data['Line'][i]
        )

# Function to find the shortest path
def find_shortest_path(graph, start, end):
    path = nx.shortest_path(graph, source=start, target=end)
    detailed_path = []
    short_path = [start]
    prev_line = None

    for i in range(len(path) - 1):
        station = path[i]
        next_station = path[i + 1]
        edge_data = graph.get_edge_data(station, next_station)
        if edge_data:
            line = list(edge_data.values())[0]['line']
            if line != prev_line:
                if prev_line:
                    detailed_path.append(f"Change to {line} line at {station} station")
                    short_path.append(f"--{prev_line} line-->")
                    short_path.append(station)
            prev_line = line
        detailed_path.append(station)
    detailed_path.append(end)
    short_path.append(f"--{line} line-->")
    short_path.append(end)
    return detailed_path, short_path

# Initialize the Flask app
app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Replace with a secure key

@app.after_request
def add_header(response):
    """Add headers to prevent caching of POST responses."""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

@app.route("/", methods=["GET", "POST"])
def hello_world():
    if request.method == "POST" and request.form['departure'] != '' and request.form['dest'] != '':
        Departure = request.form['departure']
        Destination = request.form['dest']
        Detail, Short = find_shortest_path(G, Departure, Destination)

        # Store results in session
        session['Detail'] = Detail
        session['Short'] = Short

        # Redirect to avoid form resubmission
        return redirect(url_for('hello_world'))
    else:
        # Fetch results from session if available
        Detail = session.pop('Detail', None)
        Short = session.pop('Short', None)

    return render_template('index.html', Detail=Detail, Short=Short, stat=data['Station'].tolist())

@app.route("/getlivestatus")
def livestatus():
    return render_template('livestatus.html')

@app.route("/aboutus")
def aboutUs():
    return render_template('aboutus.html')

if __name__ == "__main__":
    app.run(debug=True)
