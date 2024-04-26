const app = new Vue({
    el: '#app',
    data: {
        plantBeds: [],
        expandedBed: null,
        sensors: {},
        valves: {}
    },
    mounted() {
        this.fetchPlantBeds();
    },
    methods: {
        async fetchPlantBeds() {
            try {
                const response = await axios.get('/api/plantbed');
                this.plantBeds = response.data;
                this.fetchSensors();
                this.fetchValves();
            } catch (error) {
                console.error('Error fetching plant beds:', error);
            }
        },
        async fetchSensors() {
            try {
                const response = await axios.get('/api/sensor');
                this.sensors = response.data.reduce((acc, sensor) => {
                    acc[sensor.id] = sensor;
                    return acc;
                }, {});
            } catch (error) {
                console.error('Error fetching sensors:', error);
            }
        },
        async fetchValves() {
            try {
                const response = await axios.get('/api/valve');
                this.valves = response.data.reduce((acc, valve) => {
                    acc[valve.id] = valve;
                    return acc;
                }, {});
            } catch (error) {
                console.error('Error fetching valves:', error);
            }
        },
        toggleExpansion(bedId) {
            this.expandedBed = this.expandedBed === bedId ? null : bedId;
        },
        async toggleActive(bed) {
            try {
                await axios.put(`/api/plantbed/${bed.id}`, { ...bed, active: !bed.active });
                bed.active = !bed.active;
            } catch (error) {
                console.error('Error toggling active state:', error);
            }
        }
    }
});
