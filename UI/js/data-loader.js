/**
 * Data Loader Module
 * Handles loading and parsing CSV data files
 */

const DataLoader = {
    customerData: null,
    deviceData: null,
    nbaData: null,
    vizData: null,
    
    /**
     * Load all required data files
     */
    async loadAllData() {
        try {
            console.log('Starting to load data files...');
            
            console.log('Loading customer_data.csv...');
            const customerData = await this.loadCSV('../Data/Data Output/customer_data.csv');
            console.log(`✓ Loaded ${customerData.length} customer records`);
            
            console.log('Loading device_data.csv...');
            const deviceData = await this.loadCSV('../Data/Data Output/device_data.csv');
            console.log(`✓ Loaded ${deviceData.length} device records`);
            
            console.log('Loading nba_data.csv...');
            const nbaData = await this.loadCSV('../Data/Data Output/nba_data.csv');
            console.log(`✓ Loaded ${nbaData.length} NBA records`);
            
            console.log('Loading viz_data.csv...');
            const vizData = await this.loadCSV('../Data/Data Output/viz_data.csv');
            console.log(`✓ Loaded ${vizData.length} viz records`);
            
            this.customerData = customerData;
            this.deviceData = this.parseDeviceData(deviceData);
            this.nbaData = nbaData;
            this.vizData = this.parseVizData(vizData);
            
            console.log('✓ All data loaded successfully!');
            
            return {
                customerData: this.customerData,
                deviceData: this.deviceData,
                nbaData: this.nbaData,
                vizData: this.vizData
            };
        } catch (error) {
            console.error('❌ Error loading data:', error);
            throw new Error(`Failed to load data: ${error.message}`);
        }
    },
    
    /**
     * Load a single CSV file
     */
    async loadCSV(url) {
        const response = await fetch(url);
        if (!response.ok) {
            throw new Error(`Failed to load ${url}: ${response.statusText}`);
        }
        const text = await response.text();
        return d3.csvParse(text);
    },
    
    /**
     * Parse device data and convert date strings
     */
    parseDeviceData(data) {
        return data.map(d => ({
            ...d,
            last_alive_date: new Date(d.last_alive_date),
            ship_date: new Date(d.ship_date),
            sqs_score: +d.sqs_score
        }));
    },
    
    /**
     * Parse viz data and convert numeric values
     */
    parseVizData(data) {
        return data.map(d => ({
            quarter: d.Quarter_Label || d.quarter,
            year: +d.Year || 0,
            quarterNum: +d.Quarter || 0,
            active: +d.Active || +d.active || 0,
            inactive: +d.Inactive || +d.inactive || 0,
            type: d.Type || '',
            isForecast: d.Is_Forecast === 'True' || d.Is_Forecast === true
        }));
    },
    
    /**
     * Get merged customer and device data
     */
    getMergedData() {
        if (!this.customerData || !this.deviceData) {
            throw new Error('Data not loaded yet');
        }
        
        // Create a customer lookup map
        const customerMap = new Map();
        this.customerData.forEach(customer => {
            customerMap.set(customer.customer_id, customer);
        });
        
        // Merge device data with customer data
        return this.deviceData.map(device => {
            const customer = customerMap.get(device.customer_id) || {};
            return { ...customer, ...device };
        });
    },
    
    /**
     * Get NBA merged data - one row per device
     * Each device inherits its customer's NBA information
     */
    getNBAMergedData() {
        if (!this.nbaData || !this.deviceData) {
            throw new Error('NBA or device data not loaded yet');
        }
        
        // Create a map of customer_id to NBA info
        const nbaMap = new Map();
        this.nbaData.forEach(nba => {
            nbaMap.set(nba.customer_id, nba);
        });
        
        // Create one row per device, inheriting customer's NBA info
        const mergedData = [];
        this.deviceData.forEach(device => {
            const nbaInfo = nbaMap.get(device.customer_id);
            if (nbaInfo) {
                // Merge device info with customer's NBA info
                mergedData.push({
                    ...nbaInfo,
                    serial_number: device.serial_number,
                    device_model: device.device_model,
                    device_status: device.device_status,
                    isp: device.isp,
                    last_alive_date: device.last_alive_date,
                    ship_date: device.ship_date,
                    sqs_score: device.sqs_score
                });
            }
        });
        
        console.log(`Created ${mergedData.length} device records (one per device)`);
        return mergedData;
    }
};

// Export for use in other modules
window.DataLoader = DataLoader;
