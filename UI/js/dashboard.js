/**
 * Dashboard Module
 * Handles device overview dashboard logic
 */

const Dashboard = {
    deviceData: null,
    filteredData: null,
    activeThreshold: 30,
    filters: {
        networkActivity: null,  // e.g., 'Frontier Active'
        deviceModel: null,      // e.g., 'Eero 6'
        deviceStatus: null      // e.g., 'Provisioned'
    },
    
    /**
     * Initialize the dashboard
     */
    init(deviceData) {
        console.log('Dashboard.init called with deviceData:', deviceData ? deviceData.length : 'undefined');
        this.deviceData = deviceData;
        this.filteredData = deviceData;
        this.setupControls();
        this.updateDashboard();
    },
    
    /**
     * Setup control event listeners
     */
    setupControls() {
        // No controls needed - active threshold is fixed at 30 days
    },
    
    /**
     * Apply current filters to device data
     */
    applyFilters() {
        console.log('applyFilters called. Current filters:', this.filters);
        const currentDate = new Date();
        const thresholdMs = this.activeThreshold * 24 * 60 * 60 * 1000;
        
        this.filteredData = this.deviceData.filter(device => {
            // Filter by network activity status
            if (this.filters.networkActivity) {
                const isFrontier = device.isp === 'Frontier Communications';
                const isActive = (currentDate - device.last_alive_date) < thresholdMs;
                
                const status = isFrontier 
                    ? (isActive ? 'Frontier Active' : 'Frontier Inactive')
                    : (isActive ? 'Non-Frontier Active' : 'Non-Frontier Inactive');
                
                if (status !== this.filters.networkActivity) return false;
            }
            
            // Filter by device model
            if (this.filters.deviceModel && device.device_model !== this.filters.deviceModel) {
                return false;
            }
            
            // Filter by device status
            if (this.filters.deviceStatus && device.device_status !== this.filters.deviceStatus) {
                return false;
            }
            
            return true;
        });
        
        console.log('Filtered data:', this.filteredData.length, 'devices (from', this.deviceData.length, 'total)');
    },
    
    /**
     * Clear a specific filter
     */
    clearFilter(filterType) {
        this.filters[filterType] = null;
        this.applyFilters();
        this.updateDashboard();
    },
    
    /**
     * Set a filter and update dashboard
     */
    setFilter(filterType, value) {
        console.log('setFilter called:', filterType, value);
        // If clicking the same filter, clear it (toggle)
        if (this.filters[filterType] === value) {
            console.log('Clearing filter:', filterType);
            this.clearFilter(filterType);
        } else {
            console.log('Setting filter:', filterType, '=', value);
            this.filters[filterType] = value;
            this.applyFilters();
            this.updateDashboard();
        }
    },
    
    /**
     * Calculate statistics based on current threshold and filtered data
     */
    calculateStats() {
        const currentDate = new Date();
        const thresholdMs = this.activeThreshold * 24 * 60 * 60 * 1000;
        
        const stats = {
            total: this.filteredData.length,
            frontier: 0,
            nonFrontier: 0,
            frontierActive: 0,
            frontierInactive: 0,
            nonFrontierActive: 0,
            nonFrontierInactive: 0,
            deviceModels: {},
            deviceStatuses: {}
        };
        
        this.filteredData.forEach(device => {
            const isFrontier = device.isp === 'Frontier Communications';
            const isActive = (currentDate - device.last_alive_date) < thresholdMs;
            
            // Network activity stats
            if (isFrontier) {
                stats.frontier++;
                if (isActive) {
                    stats.frontierActive++;
                } else {
                    stats.frontierInactive++;
                }
            } else {
                stats.nonFrontier++;
                if (isActive) {
                    stats.nonFrontierActive++;
                } else {
                    stats.nonFrontierInactive++;
                }
            }
            
            // Device model distribution
            const model = device.device_model || 'Unknown';
            stats.deviceModels[model] = (stats.deviceModels[model] || 0) + 1;
            
            // Device status distribution
            const status = device.device_status || 'Unknown';
            stats.deviceStatuses[status] = (stats.deviceStatuses[status] || 0) + 1;
        });
        
        return stats;
    },
    
    /**
     * Update all dashboard visualizations
     */
    updateDashboard() {
        const stats = this.calculateStats();
        this.updateStatCards(stats);
        this.updateTreeView(stats);
        this.updateCharts(stats);
    },
    
    /**
     * Update statistic cards
     */
    updateStatCards(stats) {
        console.log('Dashboard.updateStatCards called with stats:', stats);
        const totalEl = document.getElementById('total-devices');
        const totalActiveEl = document.getElementById('total-active-devices');
        const liabilityEl = document.getElementById('expected-liability');
        
        // Total devices (all devices)
        if (totalEl) totalEl.textContent = stats.total.toLocaleString();
        
        // Total active devices (Frontier Active + Non-Frontier Active)
        const totalActive = stats.frontierActive + stats.nonFrontierActive;
        if (totalActiveEl) totalActiveEl.textContent = totalActive.toLocaleString();
        
        // Calculate expected liability based on total active devices: Total active × $6/device/year
        if (liabilityEl) {
            const licenseCostPerDevice = 6;
            const expectedLiability = totalActive * licenseCostPerDevice;
            console.log('Expected liability calculation:', totalActive, '×', licenseCostPerDevice, '=', expectedLiability);
            liabilityEl.textContent = '$' + expectedLiability.toLocaleString();
        } else {
            console.warn('Expected liability element not found');
        }
    },
    
    /**
     * Update tree visualization
     */
    updateTreeView(stats) {
        const treeHTML = `
            <div class="tree-level text-center">
                <div class="tree-node">
                    <strong>Total Devices</strong><br>
                    ${stats.total.toLocaleString()}
                </div>
            </div>
            <div style="text-align: center; font-size: 2em; color: #999; margin: 10px 0;">↓</div>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 30px; max-width: 900px; margin: 0 auto;">
                <!-- Frontier Column -->
                <div style="display: flex; flex-direction: column; align-items: stretch;">
                    <div class="tree-node frontier" style="margin-bottom: 15px;">
                        <strong>Frontier</strong><br>
                        ${stats.frontier.toLocaleString()}
                    </div>
                    <div style="text-align: center; font-size: 1.5em; color: #999; margin: 5px 0;">↓</div>
                    <div class="tree-node active target" style="margin-bottom: 10px;">
                        <strong>🎯 Active</strong><br>
                        ${stats.frontierActive.toLocaleString()}
                    </div>
                    <div class="tree-node inactive">
                        <strong>Inactive</strong><br>
                        ${stats.frontierInactive.toLocaleString()}
                    </div>
                </div>
                <!-- Non-Frontier Column -->
                <div style="display: flex; flex-direction: column; align-items: stretch;">
                    <div class="tree-node" style="margin-bottom: 15px; background: linear-gradient(135deg, #757575 0%, #616161 100%); color: white;">
                        <strong>Non-Frontier</strong><br>
                        ${stats.nonFrontier.toLocaleString()}
                    </div>
                    <div style="text-align: center; font-size: 1.5em; color: #999; margin: 5px 0;">↓</div>
                    <div class="tree-node active" style="margin-bottom: 10px;">
                        <strong>Active</strong><br>
                        ${stats.nonFrontierActive.toLocaleString()}
                    </div>
                    <div class="tree-node inactive">
                        <strong>Inactive</strong><br>
                        ${stats.nonFrontierInactive.toLocaleString()}
                    </div>
                </div>
            </div>
        `;
        
        const treeView = document.getElementById('tree-view');
        if (treeView) {
            treeView.innerHTML = treeHTML;
        }
    },
    
    /**
     * Update interactive pie charts
     */
    updateCharts(stats) {
        // 1. Network & Activity Status Chart
        const networkActivityData = [
            { label: 'Frontier Active', value: stats.frontierActive },
            { label: 'Frontier Inactive', value: stats.frontierInactive },
            { label: 'Non-Frontier Active', value: stats.nonFrontierActive },
            { label: 'Non-Frontier Inactive', value: stats.nonFrontierInactive }
        ];
        // Softer, more muted colors for better readability
        const networkColors = ['#4CAF50', '#F44336', '#2196F3', '#9C27B0'];
        Charts.drawInteractivePieChart(
            'network-activity-chart', 
            networkActivityData, 
            networkColors,
            (label) => this.setFilter('networkActivity', label),
            this.filters.networkActivity
        );
        
        // 2. Device Model Chart
        const modelData = Object.entries(stats.deviceModels)
            .map(([label, value]) => ({ label, value }))
            .sort((a, b) => b.value - a.value);
        // Professional material design colors with better contrast
        const modelColors = ['#3F51B5', '#673AB7', '#E91E63', '#FF5722', '#00BCD4', '#009688'];
        Charts.drawInteractivePieChart(
            'device-model-chart', 
            modelData, 
            modelColors,
            (label) => this.setFilter('deviceModel', label),
            this.filters.deviceModel
        );
        
        // 3. Device Status Bar Chart (Full Width)
        const statusData = Object.entries(stats.deviceStatuses)
            .map(([label, value]) => ({ label, value }))
            .sort((a, b) => b.value - a.value);
        // Balanced color palette with good visibility
        const statusColors = ['#4CAF50', '#00BCD4', '#FF9800', '#E91E63', '#9C27B0', '#607D8B'];
        Charts.drawInteractiveBarChart(
            'device-status-chart', 
            statusData, 
            statusColors,
            (label) => this.setFilter('deviceStatus', label),
            this.filters.deviceStatus
        );
    }
};

window.Dashboard = Dashboard;

