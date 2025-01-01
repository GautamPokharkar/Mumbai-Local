from flask import Flask, render_template, request
import pandas as pd
import networkx as nx

# Load the dataset
data = pd.read_csv('Mumbai Local Train Dataset.csv', encoding='latin1')

# Create a MultiGraph to store the train network
G = nx.MultiGraph()

# Standardize station names to lowercase for case-insensitive matching
data['Station'] = data['Station'].str.lower()

# Add edges between stations if they are on the same line
for i in range(154 - 1):  
    if data['Line'][i] == data['Line'][i + 1]:  
        G.add_edge(
            data['Station'][i],
            data['Station'][i + 1],
            key=f"{data['Line'][i]}_{i}",  
            line=data['Line'][i]  
        )

# Function to find the shortest path between two stations
def find_shortest_path(graph, start, end):
    # Get the shortest path (unweighted)
    path = nx.shortest_path(graph, source=start, target=end)
    detailed_path = []
    short_path = []
    short_path.append(start)
    prev_line = None

    # Process the path to track line changes
    for i in range(len(path) - 1):
        station = path[i]
        next_station = path[i + 1]
        
        # Access edge attributes (line) from MultiGraph
        edge_data = graph.get_edge_data(station, next_station)
        if edge_data:
            # Extract the line attribute (fetch from the first edge, assuming one exists)
            line = list(edge_data.values())[0]['line']
            if line != prev_line:
                if prev_line:  # Only add this if it's not the first station
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

# Home route to process the search
@app.route("/", methods=["GET", "POST"])
def hello_world():
    if request.method == "POST" and request.form['departure'] != '' and request.form['dest'] != '':
        # Standardize the input station names to lowercase
        Departure = request.form['departure'].lower()  # Convert to lowercase
        Destination = request.form['dest'].lower()  # Convert to lowercase
        
        # Ensure the stations exist in the graph (case insensitive)
        if Departure in G.nodes and Destination in G.nodes:
            Detail, Short = find_shortest_path(G, Departure, Destination)
            return render_template('index.html', Detail=Detail, Short=Short, stat=data['Station'].tolist())
        else:
            # If the station doesn't exist in the graph, show an error
            return render_template('index.html', error="Station not found. Please enter a valid station name.")
    
    return render_template('index.html')

# Route for live status page
@app.route("/getlivestatus")
def livestatus():
    return render_template('livestatus.html')

# Route for about us page
@app.route("/aboutus")
def aboutUs():
    return render_template('aboutus.html')

# Run the app
if __name__ == "__main__":
    app.run(debug=True)
