/**
 * Next Best Action Module
 * Handles NBA logic and visualization
 */

const NBA = {
    nbaData: [],
    filteredData: [],
    currentFilter: 'all',
    activeThreshold: 30, // days - matches dashboard default
    originalDeviceCount: 0, // Store original count before filtering
    originalData: [], // Store original unfiltered data
    totalActiveDeviceCount: 0, // Store total active devices count
    frontierActiveDeviceCount: 0, // Store Frontier Active devices count
    
    // Simulation parameters
    simulationParams: {
        takeRateUpgradeOnly: 3,
        takeRateUpgradeDevice: 5,
        licenseCostYearly: 6
    },
    
    /**
     * Initialize NBA module
     */
    init(nbaData) {
        // Store original data and device count before filtering
        this.originalData = nbaData;
        this.originalDeviceCount = nbaData.length;
        
        // Calculate total active devices (both Frontier and Non-Frontier)
        this.totalActiveDeviceCount = this.countActiveDevices(nbaData);
        
        // Filter for Frontier network and active devices only
        this.nbaData = this.filterFrontierActive(nbaData);
        this.filteredData = this.nbaData;
        
        // Store Frontier Active device count
        this.frontierActiveDeviceCount = this.nbaData.length;
        
        this.setupControls();
        this.updateNBAView();
    },
    
    /**
     * Count total active devices across all ISPs
     */
    countActiveDevices(data) {
        const currentDate = new Date();
        const thresholdMs = this.activeThreshold * 24 * 60 * 60 * 1000;
        
        return data.filter(device => {
            const isActive = (currentDate - device.last_alive_date) < thresholdMs;
            return isActive;
        }).length;
    },
    
    /**
     * Filter data to only include Frontier network and active devices
     */
    filterFrontierActive(data) {
        const currentDate = new Date();
        const thresholdMs = this.activeThreshold * 24 * 60 * 60 * 1000;
        
        return data.filter(device => {
            // Must be on Frontier network
            const isFrontier = device.isp === 'Frontier Communications';
            
            // Must be active (last alive within threshold)
            const isActive = (currentDate - device.last_alive_date) < thresholdMs;
            
            return isFrontier && isActive;
        });
    },
    
    /**
     * Setup control event listeners
     */
    setupControls() {
        const filterSelect = document.getElementById('nba-filter');
        const customerSearchInput = document.getElementById('customer-search');
        const serialSearchInput = document.getElementById('serial-search');
        
        // Download buttons for each disposition
        const downloadShipDeviceBtn = document.getElementById('download-ship-device');
        const downloadUpgradeDeviceBtn = document.getElementById('download-upgrade-device');
        const downloadUpgradeOnlyBtn = document.getElementById('download-upgrade-only');
        const downloadKeepAsIsBtn = document.getElementById('download-keep-as-is');
        
        if (filterSelect) {
            filterSelect.addEventListener('change', (e) => {
                this.currentFilter = e.target.value;
                this.filterData();
                this.updateNBAView();
            });
        }
        
        if (customerSearchInput) {
            customerSearchInput.addEventListener('input', (e) => {
                this.searchData(e.target.value, 'customer');
            });
        }
        
        if (serialSearchInput) {
            serialSearchInput.addEventListener('input', (e) => {
                this.searchData(e.target.value, 'serial');
            });
        }
        
        // Setup download button event listeners for each disposition
        if (downloadShipDeviceBtn) {
            downloadShipDeviceBtn.addEventListener('click', () => {
                this.downloadCSV('Ship new device');
            });
        }
        
        if (downloadUpgradeDeviceBtn) {
            downloadUpgradeDeviceBtn.addEventListener('click', () => {
                this.downloadCSV('Speed upgrade + new device');
            });
        }
        
        if (downloadUpgradeOnlyBtn) {
            downloadUpgradeOnlyBtn.addEventListener('click', () => {
                this.downloadCSV('Speed upgrade only');
            });
        }
        
        if (downloadKeepAsIsBtn) {
            downloadKeepAsIsBtn.addEventListener('click', () => {
                this.downloadCSV('Keep as is');
            });
        }
        
        // Simulation controls
        this.setupSimulationControls();
    },
    
    /**
     * Setup simulation control event listeners
     */
    setupSimulationControls() {
        const takeRateUpgradeOnlySlider = document.getElementById('take-rate-upgrade-only');
        const takeRateUpgradeDeviceSlider = document.getElementById('take-rate-upgrade-device');
        const runSimButton = document.getElementById('run-simulation');
        
        if (takeRateUpgradeOnlySlider) {
            takeRateUpgradeOnlySlider.addEventListener('input', (e) => {
                this.simulationParams.takeRateUpgradeOnly = parseFloat(e.target.value);
                document.getElementById('take-rate-upgrade-only-value').textContent = e.target.value;
            });
        }
        
        if (takeRateUpgradeDeviceSlider) {
            takeRateUpgradeDeviceSlider.addEventListener('input', (e) => {
                this.simulationParams.takeRateUpgradeDevice = parseFloat(e.target.value);
                document.getElementById('take-rate-upgrade-device-value').textContent = e.target.value;
            });
        }
        
        if (runSimButton) {
            runSimButton.addEventListener('click', () => {
                this.runSimulation();
            });
        }
    },
    
    /**
     * Run the simulation based on current parameters
     */
    runSimulation() {
        // Use yearly license cost ($6.00 per device per year)
        const licenseCost = this.simulationParams.licenseCostYearly;
        
        // Group devices by customer to handle "upgrade all devices" scenario
        const customerDevices = {};
        this.nbaData.forEach(d => {
            if (!customerDevices[d.customer_id]) {
                customerDevices[d.customer_id] = [];
            }
            customerDevices[d.customer_id].push(d);
        });
        
        // Count unique customers by action type (one recommendation per customer)
        const customerActions = {};
        Object.entries(customerDevices).forEach(([customerId, devices]) => {
            // Take the first device's action as the customer action
            const action = devices[0].next_best_action;
            if (!customerActions[action]) {
                customerActions[action] = [];
            }
            customerActions[action].push({ customerId, deviceCount: devices.length });
        });
        
        // Calculate results for each action type
        const results = {};
        
        // Speed upgrade only: If accepted, keeps devices and renews licenses; if not accepted, still needs licenses
        if (customerActions['Speed upgrade only']) {
            const eligible = customerActions['Speed upgrade only'];
            const totalEligibleDevices = eligible.reduce((sum, c) => sum + c.deviceCount, 0);
            const conversions = Math.round(eligible.length * this.simulationParams.takeRateUpgradeOnly / 100);
            const avgDevicesPerCustomer = totalEligibleDevices / eligible.length;
            
            // ALL devices need licenses (whether customer accepts upgrade or not - they keep devices)
            const devicesAffected = totalEligibleDevices;
            
            results['Speed upgrade only'] = {
                eligible: eligible.length,
                takeRate: this.simulationParams.takeRateUpgradeOnly,
                conversions: conversions,
                devicesAffected: devicesAffected,
                licenseCostPerDevice: licenseCost,
                totalLicenseCost: devicesAffected * licenseCost,
                note: `${conversions} customers accept upgrade, but all ${devicesAffected} devices need licenses`
            };
        }
        
        // Speed upgrade + new device: If accepted, gets new devices (no license); if not accepted, needs licenses
        if (customerActions['Speed upgrade + new device']) {
            const eligible = customerActions['Speed upgrade + new device'];
            const totalEligibleDevices = eligible.reduce((sum, c) => sum + c.deviceCount, 0);
            const conversions = Math.round(eligible.length * this.simulationParams.takeRateUpgradeDevice / 100);
            const nonConversions = eligible.length - conversions;
            const avgDevicesPerCustomer = totalEligibleDevices / eligible.length;
            
            // Only non-converted customers need licenses (converted customers get new devices)
            const devicesNeedingLicense = Math.round(nonConversions * avgDevicesPerCustomer);
            const devicesGettingNew = Math.round(conversions * avgDevicesPerCustomer);
            
            results['Speed upgrade + new device'] = {
                eligible: eligible.length,
                takeRate: this.simulationParams.takeRateUpgradeDevice,
                conversions: conversions,
                devicesAffected: totalEligibleDevices,
                devicesGettingNew: devicesGettingNew,
                devicesNeedingLicense: devicesNeedingLicense,
                licenseCostPerDevice: licenseCost,
                totalLicenseCost: devicesNeedingLicense * licenseCost,
                note: `${conversions} customers get new devices (${devicesGettingNew} devices), ${nonConversions} customers need licenses (${devicesNeedingLicense} devices)`
            };
        }
        
        // Ship new device: No license fee (new device shipped)
        if (customerActions['Ship new device']) {
            const eligible = customerActions['Ship new device'];
            const conversions = eligible.length; // 100% take rate
            const devicesAffected = eligible.reduce((sum, c) => sum + c.deviceCount, 0);
            
            results['Ship new device'] = {
                eligible: eligible.length,
                takeRate: 100,
                conversions: conversions,
                devicesAffected: devicesAffected,
                licenseCostPerDevice: 0,
                totalLicenseCost: 0,
                note: 'New devices shipped to all customers, no license cost'
            };
        }
        
        // Keep as is: Count towards liability (need to maintain licenses)
        if (customerActions['Keep as is']) {
            const eligible = customerActions['Keep as is'];
            const conversions = eligible.length;
            const devicesAffected = eligible.reduce((sum, c) => sum + c.deviceCount, 0);
            
            results['Keep as is'] = {
                eligible: eligible.length,
                takeRate: 100,
                conversions: conversions,
                devicesAffected: devicesAffected,
                licenseCostPerDevice: licenseCost,
                totalLicenseCost: devicesAffected * licenseCost,
                note: `All ${conversions} customers maintain devices, ${devicesAffected} devices need licenses`
            };
        }
        
        // Calculate totals
        let totalLiability = 0;
        let totalDevicesWithLicenses = 0;
        let totalConversions = 0;
        
        Object.entries(results).forEach(([action, r]) => {
            totalLiability += r.totalLicenseCost;
            
            // For devices needing licenses, use specific count if available (Speed upgrade + new device)
            // Otherwise use devicesAffected if license cost > 0
            if (r.devicesNeedingLicense !== undefined) {
                totalDevicesWithLicenses += r.devicesNeedingLicense;
            } else if (r.licenseCostPerDevice > 0) {
                totalDevicesWithLicenses += r.devicesAffected;
            }
            
            // Only count conversions for Speed Upgrade actions
            if (action === 'Speed upgrade only' || action === 'Speed upgrade + new device') {
            totalConversions += r.conversions;
            }
        });
        
        // Update UI
        this.displaySimulationResults(results, totalConversions, totalLiability, totalDevicesWithLicenses, licenseCost);
    },
    
    /**
     * Display simulation results
     */
    displaySimulationResults(results, totalConversions, totalLiability, totalDevicesWithLicenses, licenseCost) {
        // Show results section
        const resultsSection = document.getElementById('simulation-results');
        if (resultsSection) {
            resultsSection.style.display = 'block';
        }
        
        // Update main liability display
        const totalLiabilityEl = document.getElementById('sim-total-liability');
        const liabilityPeriodEl = document.getElementById('liability-period');
        const liabilityDetailEl = document.getElementById('liability-detail');
        
        if (totalLiabilityEl) {
            totalLiabilityEl.textContent = '$' + totalLiability.toLocaleString();
        }
        
        if (liabilityPeriodEl) {
            liabilityPeriodEl.textContent = 'Per Year';
        }
        
        if (liabilityDetailEl) {
            liabilityDetailEl.textContent = `${totalDevicesWithLicenses.toLocaleString()} devices requiring licenses`;
        }
        
        // Update current liability card (before simulation actions)
        const currentLiabilityEl = document.getElementById('sim-current-liability');
        const currentLiabilityDetailEl = document.getElementById('current-liability-detail');
        
        // Use Frontier Active devices only
        const currentLiability = this.frontierActiveDeviceCount * licenseCost;
        
        if (currentLiabilityEl) {
            currentLiabilityEl.textContent = '$' + currentLiability.toLocaleString();
        }
        
        if (currentLiabilityDetailEl) {
            currentLiabilityDetailEl.textContent = `${this.frontierActiveDeviceCount.toLocaleString()} devices requiring licenses`;
        }
        
        // Update liability change card
        const liabilityChangeCard = document.getElementById('liability-change-card');
        const liabilityChangePercentEl = document.getElementById('liability-change-percent');
        const liabilityChangeDetailEl = document.getElementById('liability-change-detail');
        
        if (currentLiability > 0) {
            const change = totalLiability - currentLiability;
            const percentChange = ((change / currentLiability) * 100).toFixed(1);
            const absChange = Math.abs(change);
            
            // Update the main number (dollar amount saved/increased)
            if (liabilityChangePercentEl) {
                const sign = change > 0 ? '+' : '-';
                liabilityChangePercentEl.textContent = `${sign}$${absChange.toLocaleString()}`;
            }
            
            // Update the detail text (percentage)
            if (liabilityChangeDetailEl) {
                const sign = change > 0 ? '+' : '';
                if (change < 0) {
                    liabilityChangeDetailEl.textContent = `${sign}${percentChange}% reduction annually`;
                } else if (change > 0) {
                    liabilityChangeDetailEl.textContent = `${sign}${percentChange}% increase in costs`;
                } else {
                    liabilityChangeDetailEl.textContent = `0% - No change from baseline`;
                }
            }
            
            // Update card styling based on change
            if (liabilityChangeCard) {
                if (change < 0) {
                    // Savings - use muted teal gradient
                    liabilityChangeCard.style.background = 'linear-gradient(135deg, #28a745 0%, #218838 100%)';
                    liabilityChangeCard.style.boxShadow = '0 8px 20px rgba(40, 167, 69, 0.25)';
                } else if (change > 0) {
                    // Increase - use muted orange gradient
                    liabilityChangeCard.style.background = 'linear-gradient(135deg, #fd7e14 0%, #e66a0a 100%)';
                    liabilityChangeCard.style.boxShadow = '0 8px 20px rgba(253, 126, 20, 0.25)';
                } else {
                    // No change - use gray gradient
                    liabilityChangeCard.style.background = 'linear-gradient(135deg, #6c757d 0%, #5a6268 100%)';
                    liabilityChangeCard.style.boxShadow = '0 8px 20px rgba(108, 117, 125, 0.25)';
                }
            }
        }
        
        // Update revenue increase card
        const revenueIncreaseEl = document.getElementById('sim-revenue-increase');
        const conversionDetailEl = document.getElementById('sim-conversion-detail');
        
        // Calculate annual revenue increase: conversions × $15/month × 12 months
        const monthlyRevenuePerConversion = 15;
        const annualRevenueIncrease = totalConversions * monthlyRevenuePerConversion * 12;
        
        if (revenueIncreaseEl) {
            revenueIncreaseEl.textContent = '$' + annualRevenueIncrease.toLocaleString();
        }
        
        if (conversionDetailEl) {
            conversionDetailEl.textContent = `${totalConversions.toLocaleString()} expected conversions`;
        }
        
        // Update breakdown table
        this.updateSimulationBreakdown(results);
    },
    
    /**
     * Update simulation breakdown table
     */
    updateSimulationBreakdown(results) {
        const tbody = document.getElementById('simulation-breakdown');
        if (!tbody) return;
        
        const rows = Object.entries(results).map(([action, data]) => {
            // Build device info text
            let deviceInfo = `${data.devicesAffected.toLocaleString()} total devices`;
            if (data.devicesGettingNew !== undefined) {
                deviceInfo = `${data.devicesGettingNew.toLocaleString()} get new, ${data.devicesNeedingLicense.toLocaleString()} need licenses`;
            }
            
            return `
                <tr>
                    <td><strong>${action}</strong></td>
                    <td>${data.eligible.toLocaleString()}</td>
                    <td>${data.takeRate.toFixed(1)}%</td>
                    <td><strong>${data.conversions.toLocaleString()}</strong></td>
                    <td>
                        $${data.licenseCostPerDevice.toFixed(2)} per device
                        <br><small style="color: #666;">(${deviceInfo})</small>
                    </td>
                    <td>
                        <strong>$${data.totalLicenseCost.toLocaleString()}</strong>
                        <br><small style="color: #666;">${data.note}</small>
                    </td>
                </tr>
            `;
        }).join('');
        
        tbody.innerHTML = rows;
    },
    
    /**
     * Filter data based on selected action
     */
    filterData() {
        if (this.currentFilter === 'all') {
            this.filteredData = this.nbaData;
        } else {
            this.filteredData = this.nbaData.filter(d => 
                d.next_best_action === this.currentFilter
            );
        }
    },
    
    /**
     * Search data by customer ID or serial number
     */
    searchData(searchTerm, searchType) {
        const customerSearchInput = document.getElementById('customer-search');
        const serialSearchInput = document.getElementById('serial-search');
        
        const customerSearch = customerSearchInput ? customerSearchInput.value : '';
        const serialSearch = serialSearchInput ? serialSearchInput.value : '';
        
        if (!customerSearch && !serialSearch) {
            // No search terms, show filtered data based on action
            this.filterData();
        } else {
            // Apply both search filters
            this.filteredData = this.nbaData.filter(d => {
                const matchesCustomer = !customerSearch || d.customer_id.toString().includes(customerSearch);
                const matchesSerial = !serialSearch || (d.serial_number && d.serial_number.toString().includes(serialSearch));
                return matchesCustomer && matchesSerial;
            });
        }
        this.updateTable();
    },
    
    /**
     * Update all NBA visualizations
     */
    updateNBAView() {
        this.updateLiabilityComparison();
        this.updateStats();
        this.updateDistributionChart();
        this.updateTable();
    },
    
    /**
     * Update liability comparison section
     */
    updateLiabilityComparison() {
        const licenseCostPerDevice = 6;
        
        // Original liability: All devices before filtering
        const originalLiability = this.originalDeviceCount * licenseCostPerDevice;
        
        // Current liability: Frontier Active devices only
        const currentLiability = this.frontierActiveDeviceCount * licenseCostPerDevice;
        
        // Calculate savings
        const savings = originalLiability - currentLiability;
        const savingsPercentage = originalLiability > 0 ? ((savings / originalLiability) * 100).toFixed(1) : 0;
        
        // Update DOM elements
        const originalLiabilityEl = document.getElementById('original-liability');
        const originalDeviceCountEl = document.getElementById('original-device-count');
        const currentLiabilityEl = document.getElementById('current-liability');
        const currentDeviceCountEl = document.getElementById('current-device-count');
        const savingsEl = document.getElementById('liability-savings');
        const savingsPercentageEl = document.getElementById('savings-percentage');
        
        if (originalLiabilityEl) originalLiabilityEl.textContent = '$' + originalLiability.toLocaleString();
        if (originalDeviceCountEl) originalDeviceCountEl.textContent = `${this.originalDeviceCount.toLocaleString()} devices × $6.00/year`;
        
        if (currentLiabilityEl) currentLiabilityEl.textContent = '$' + currentLiability.toLocaleString();
        if (currentDeviceCountEl) currentDeviceCountEl.textContent = `${this.frontierActiveDeviceCount.toLocaleString()} devices × $6.00/year`;
        
        if (savingsEl) savingsEl.textContent = '$' + savings.toLocaleString();
        if (savingsPercentageEl) savingsPercentageEl.textContent = `${savingsPercentage}% reduction`;
    },
    
    /**
     * Update statistics cards
     */
    updateStats() {
        // Count unique customers (not devices)
        const uniqueCustomers = new Set(this.nbaData.map(d => d.customer_id));
        const total = uniqueCustomers.size;
        
        // For filtered count, also count unique customers
        const uniqueFilteredCustomers = new Set(this.filteredData.map(d => d.customer_id));
        const filtered = uniqueFilteredCustomers.size;
        
        // Count by action type - group by unique customers
        const customerDevices = {};
        this.nbaData.forEach(d => {
            if (!customerDevices[d.customer_id]) {
                customerDevices[d.customer_id] = d.next_best_action;
            }
        });
        
        const actionCounts = {};
        Object.values(customerDevices).forEach(action => {
            actionCounts[action] = (actionCounts[action] || 0) + 1;
        });
        
        const totalEl = document.getElementById('total-customers');
        const filteredEl = document.getElementById('filtered-customers');
        
        if (totalEl) totalEl.textContent = total.toLocaleString();
        if (filteredEl) filteredEl.textContent = filtered.toLocaleString();
    },
    
    /**
     * Update distribution chart - count by unique customers (not devices)
     */
    updateDistributionChart() {
        // Group devices by customer to count unique customers
        const customerDevices = {};
        this.nbaData.forEach(d => {
            if (!customerDevices[d.customer_id]) {
                customerDevices[d.customer_id] = [];
            }
            customerDevices[d.customer_id].push(d);
        });
        
        // Count unique customers by action type (one recommendation per customer)
        const actionCounts = {};
        Object.entries(customerDevices).forEach(([customerId, devices]) => {
            // Take the first device's action as the customer action
            const action = devices[0].next_best_action;
            actionCounts[action] = (actionCounts[action] || 0) + 1;
        });
        
        const chartData = Object.entries(actionCounts).map(([label, value]) => ({
            label,
            value
        })).sort((a, b) => b.value - a.value);
        
        const colorMap = {
            'Ship new device': '#dc3545',
            'Speed upgrade + new device': '#28a745',
            'Speed upgrade only': '#007bff',
            'Keep as is': '#6c757d'
        };
        
        Charts.drawBarChart('nba-distribution-chart', chartData, colorMap);
    },
    
    /**
     * Update customer table
     */
    updateTable() {
        const tbody = document.getElementById('nba-table-body');
        const showingCount = document.getElementById('showing-count');
        
        if (!tbody) return;
        
        const displayData = this.filteredData.slice(0, 100); // Show first 100
        
        const rows = displayData.map(d => {
            const badgeClass = this.getActionBadgeClass(d.next_best_action);
            return `
                <tr>
                    <td>${d.customer_id}</td>
                    <td>${d.serial_number || 'N/A'}</td>
                    <td><span class="badge ${badgeClass}">${d.next_best_action}</span></td>
                    <td>${d.customer_segment}</td>
                    <td>${d.clv_decile}</td>
                    <td>${d.churn_risk}</td>
                    <td>${d.sqs_score}</td>
                    <td>${d.broadband_type}</td>
                    <td>${d.current_bb_speed}</td>
                    <td>${d.device_model}</td>
                    <td>${d.device_status}</td>
                    <td>${d.isp}</td>
                </tr>
            `;
        }).join('');
        
        tbody.innerHTML = rows;
        
        // Update showing count
        if (showingCount) {
            showingCount.textContent = 
                `Showing ${displayData.length} of ${this.filteredData.length} devices`;
        }
    },
    
    /**
     * Get badge class for action type
     */
    getActionBadgeClass(action) {
        const classMap = {
            'Ship new device': 'urgent',
            'Speed upgrade + new device': 'high-value',
            'Speed upgrade only': 'medium',
            'Keep as is': 'stable'
        };
        return classMap[action] || 'stable';
    },
    
    /**
     * Download filtered data as CSV by disposition
     * @param {string} disposition - The next_best_action to filter by
     */
    downloadCSV(disposition) {
        // Filter data by the specified disposition
        const filteredByDisposition = this.filteredData.filter(row => 
            row.next_best_action === disposition
        );
        
        if (filteredByDisposition.length === 0) {
            alert(`No customers found with disposition: "${disposition}"`);
            return;
        }
        
        const headers = [
            'customer_id', 'serial_number', 'next_best_action', 'customer_segment', 'clv_decile',
            'churn_risk', 'sqs_score', 'broadband_type', 'current_bb_speed',
            'device_model', 'device_status', 'isp'
        ];
        
        let csv = headers.join(',') + '\n';
        
        filteredByDisposition.forEach(row => {
            const values = headers.map(header => {
                const value = row[header] || '';
                return `"${value}"`;
            });
            csv += values.join(',') + '\n';
        });
        
        const blob = new Blob([csv], { type: 'text/csv' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        
        const timestamp = new Date().toISOString().replace(/[:.]/g, '-').slice(0, -5);
        const dispositionName = disposition.replace(/ /g, '_').toLowerCase();
        a.href = url;
        a.download = `nba_${dispositionName}_${timestamp}.csv`;
        
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);
        
        console.log(`Downloaded ${filteredByDisposition.length} records for disposition: ${disposition}`);
    }
};

window.NBA = NBA;

