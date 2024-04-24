function PlantBed({ bed }) {
    const [expanded, setExpanded] = React.useState(false);
    const [sensor, setSensor] = React.useState(null);
    const [valve, setValve] = React.useState(null);

    React.useEffect(() => {
        fetchSensor();
        fetchValve();
    }, []);

    const fetchSensor = async () => {
        try {
            const response = await axios.get(`/api/sensor/${bed.sensor_id}`);
            setSensor(response.data);
        } catch (error) {
            console.error('Error fetching sensor:', error);
        }
    };

    const fetchValve = async () => {
        try {
            const response = await axios.get(`/api/valve/${bed.valve_id}`);
            setValve(response.data);
        } catch (error) {
            console.error('Error fetching valve:', error);
        }
    };

    const toggleExpansion = () => {
        setExpanded(!expanded);
    };

    return (
        <div className="plant-bed">
            <div>
                <strong>Name:</strong> {bed.name}
            </div>
            <div>
                <button onClick={toggleExpansion}>{expanded ? 'Hide Details' : 'Show Details'}</button>
            </div>
            {expanded && (
                <div className="details">
                    <div>
                        <strong>Valve ID:</strong> {bed.valve_id}
                    </div>
                    <div>
                        <strong>Valve Name:</strong> {valve ? valve.name : 'Loading...'}
                    </div>
                    <div>
                        <strong>Sensor ID:</strong> {bed.sensor_id}
                    </div>
                    <div>
                        <strong>Sensor Name:</strong> {sensor ? sensor.name : 'Loading...'}
                    </div>
                    <div>
                        <strong>Active:</strong> {bed.active ? 'Yes' : 'No'}
                    </div>
                </div>
            )}
        </div>
    );
}

function App() {
    const [plantBeds, setPlantBeds] = React.useState([]);

    React.useEffect(() => {
        fetchPlantBeds();
    }, []);

    const fetchPlantBeds = async () => {
        try {
            const response = await axios.get('/api/plantbed');
            setPlantBeds(response.data);
        } catch (error) {
            console.error('Error fetching plant beds:', error);
        }
    };

    return (
        <div>
            <h1>Plant Beds</h1>
            {plantBeds.map((bed) => (
                <PlantBed key={bed.id} bed={bed} />
            ))}
        </div>
    );
}

ReactDOM.render(<App />, document.getElementById('root'));
