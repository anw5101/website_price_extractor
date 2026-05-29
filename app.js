/**
 * PriceTrack Dashboard Controller
 * Vanilla ES6 Logic with dynamic state filtering, metrics rendering, and ChartJS integration.
 */

document.addEventListener("DOMContentLoaded", () => {
    // 1. STATE CONFIGURATION
    let allProducts = [];
    let filteredProducts = [];
    let selectedProduct = null;
    let priceChartInstance = null;
    
    // Active filters state
    let activeStore = "all";
    let activeStatus = "all";
    let searchQuery = "";

    // DOM Elements
    const productsGrid = document.getElementById("products-grid");
    const searchInput = document.getElementById("search-input");
    const storeFiltersContainer = document.getElementById("store-filters");
    const statusFiltersContainer = document.getElementById("status-filters");
    const resultsCountEl = document.getElementById("results-count");
    
    // KPI Counters
    const kpiTotalEl = document.getElementById("kpi-total-items");
    const kpiHealthyEl = document.getElementById("kpi-healthy");
    const kpiAnomaliesEl = document.getElementById("kpi-anomalies");
    const kpiAvgPriceEl = document.getElementById("kpi-avg-price");
    const lastUpdatedEl = document.getElementById("last-updated-time");

    // Chart Panel Elements
    const chartPanel = document.getElementById("chart-panel");
    const chartPlaceholder = document.getElementById("chart-placeholder");
    const canvasWrapper = document.querySelector(".canvas-wrapper");
    const chartProdName = document.getElementById("chart-product-name");
    const chartProdUrl = document.getElementById("chart-product-url");
    const chartProdPrice = document.getElementById("chart-product-price");
    
    const chartFooterMeta = document.getElementById("chart-footer-meta");
    const chartMetaChange = document.getElementById("chart-meta-change");
    const chartMetaStore = document.getElementById("chart-meta-store");
    const chartMetaStatus = document.getElementById("chart-meta-status");

    // ==========================================================================
    // 2. DATA LOAD & BOOTSTRAPPING
    // ==========================================================================
    function bootstrap() {
        // Check if priceTrackerData was successfully loaded from local data.js script
        if (typeof priceTrackerData !== "undefined" && Array.isArray(priceTrackerData)) {
            console.log("Successfully loaded local script data bundle.");
            allProducts = priceTrackerData;
            initializeDashboard();
        } else {
            // Try fetching dynamically (e.g. if running on standard local web server)
            console.warn("data.js not found or uninitialized. Attempting data.json fetch fallback...");
            fetch("data.json")
                .then(res => res.json())
                .then(data => {
                    allProducts = data;
                    initializeDashboard();
                })
                .catch(err => {
                    console.error("CORS Block or data.json file missing:", err);
                    renderErrorState();
                });
        }
    }

    function initializeDashboard() {
        // Build dynamic store filters list from unique domains
        buildStoreFilters();
        
        // Calculate & render KPI analytics
        calculateKPIs();
        
        // Initial products render
        applyFiltersAndRender();
        
        // Setup interactive listeners
        setupEventListeners();
        
        // Set last updated time stamp
        if (allProducts.length > 0 && allProducts[0].last_updated) {
            lastUpdatedEl.textContent = allProducts[0].last_updated;
        } else {
            lastUpdatedEl.textContent = new Date().toLocaleString();
        }
        
        // Initialize vector icons
        lucide.createIcons();
    }

    function renderErrorState() {
        productsGrid.innerHTML = `
            <div class="loading-state text-danger" style="grid-column: span 3; padding: 3rem;">
                <i data-lucide="shield-alert" style="width: 48px; height: 48px; margin: 0 auto 1rem; display: block;"></i>
                <h4>Scraper Data Missing</h4>
                <p style="max-width: 320px; margin: 0.5rem auto 0; font-size: 0.85rem; color: var(--text-secondary);">
                    The local price registry is empty. Run the scraper script using <code>python price_extractor_manual_excel_input.py</code> in your terminal to compile the database first!
                </p>
            </div>
        `;
        lucide.createIcons();
    }

    // ==========================================================================
    // 3. STATISTICAL & KPI CALCULATIONS
    // ==========================================================================
    function calculateKPIs() {
        let total = allProducts.length;
        let healthy = 0;
        let anomalies = 0;
        let priceSum = 0;
        let priceCount = 0;

        allProducts.forEach(item => {
            if (item.status === "active") {
                healthy++;
            } else if (item.status === "xpath_error" || item.status === "blocked" || item.status === "failed" || item.status === "invalid_data") {
                anomalies++;
            }

            // Extract numeric pricing if valid
            if (item.current_price && item.current_price !== "Not found") {
                // Find clean numerical value from history if it exists
                if (item.history && item.history.length > 0) {
                    let latest = item.history[item.history.length - 1];
                    priceSum += latest.price;
                    priceCount++;
                }
            }
        });

        // Populate elements
        kpiTotalEl.textContent = total;
        kpiHealthyEl.textContent = healthy;
        kpiAnomaliesEl.textContent = anomalies;
        
        if (priceCount > 0) {
            let avg = priceSum / priceCount;
            kpiAvgPriceEl.textContent = `$${avg.toFixed(2)}`;
        } else {
            kpiAvgPriceEl.textContent = "$0.00";
        }
    }

    // ==========================================================================
    // 4. DYNAMIC FILTERS & RENDERING
    // ==========================================================================
    function buildStoreFilters() {
        // Extract distinct non-empty domains
        const domains = [...new Set(allProducts.map(p => p.domain).filter(Boolean))];
        
        domains.forEach(domain => {
            const btn = document.createElement("button");
            btn.className = "filter-btn";
            btn.setAttribute("data-store", domain);
            
            // Assign beautiful Lucide icons depending on store
            let iconStr = "store";
            if (domain.includes("amazon")) iconStr = "shopping-bag";
            else if (domain.includes("hy-vee")) iconStr = "shopping-cart";
            else if (domain.includes("homedepot")) iconStr = "home";
            else if (domain.includes("menards")) iconStr = "wrench";
            else if (domain.includes("kwiktrip")) iconStr = "fuel";
            
            btn.innerHTML = `<i data-lucide="${iconStr}"></i> ${domain}`;
            storeFiltersContainer.appendChild(btn);
        });
    }

    function applyFiltersAndRender() {
        // Filter by Search Query, Store domain, and Health Status
        filteredProducts = allProducts.filter(item => {
            const matchesSearch = item.name.toLowerCase().includes(searchQuery.toLowerCase()) || 
                                  item.url.toLowerCase().includes(searchQuery.toLowerCase());
            
            const matchesStore = activeStore === "all" || item.domain === activeStore;
            
            // Status matches
            let matchesStatus = activeStatus === "all";
            if (activeStatus === "active") {
                matchesStatus = item.status === "active";
            } else if (activeStatus === "xpath_error") {
                matchesStatus = item.status === "xpath_error";
            } else if (activeStatus === "blocked") {
                matchesStatus = item.status === "blocked" || item.status === "failed" || item.status === "invalid_data";
            }

            return matchesSearch && matchesStore && matchesStatus;
        });

        // Update count tag
        resultsCountEl.textContent = `Showing ${filteredProducts.length} of ${allProducts.length} items`;
        
        // Render
        renderProductGrid();
    }

    function calculatePriceTrend(history) {
        if (!history || history.length < 2) {
            return { direction: "flat", diffPercent: 0, class: "flat", icon: "minus" };
        }
        
        const lastVal = history[history.length - 1].price;
        const prevVal = history[history.length - 2].price;
        
        if (lastVal < prevVal) {
            let pct = ((prevVal - lastVal) / prevVal) * 100;
            return { direction: "down", diffPercent: pct.toFixed(1), class: "down", icon: "trending-down" };
        } else if (lastVal > prevVal) {
            let pct = ((lastVal - prevVal) / prevVal) * 100;
            return { direction: "up", diffPercent: pct.toFixed(1), class: "up", icon: "trending-up" };
        }
        
        return { direction: "flat", diffPercent: 0, class: "flat", icon: "minus" };
    }

    function renderProductGrid() {
        if (filteredProducts.length === 0) {
            productsGrid.innerHTML = `
                <div class="loading-state" style="grid-column: span 3; padding: 4rem 2rem;">
                    <i data-lucide="info" style="width: 32px; height: 32px; margin: 0 auto 0.5rem; display: block; color: var(--text-tertiary);"></i>
                    <p>No products match the selected search or filters.</p>
                </div>
            `;
            lucide.createIcons();
            return;
        }

        productsGrid.innerHTML = "";
        
        filteredProducts.forEach(prod => {
            const card = document.createElement("div");
            
            // Build classes based on active state
            let statusClass = "status-" + prod.status;
            if (prod.status === "failed" || prod.status === "invalid_data") statusClass = "status-blocked";
            
            card.className = `product-card ${statusClass}`;
            if (selectedProduct && selectedProduct.url === prod.url) {
                card.classList.add("selected");
            }
            
            // Price Trend Sparkline
            const trend = calculatePriceTrend(prod.history);
            let trendHtml = "";
            if (prod.status === "active") {
                if (trend.direction !== "flat") {
                    trendHtml = `
                        <div class="trend-badge ${trend.class}">
                            <i data-lucide="${trend.icon}"></i>
                            <span>${trend.diffPercent}%</span>
                        </div>
                    `;
                } else {
                    trendHtml = `
                        <div class="trend-badge flat">
                            <i data-lucide="minus"></i>
                            <span>Stable</span>
                        </div>
                    `;
                }
            } else {
                trendHtml = `
                    <div class="trend-badge flat text-danger">
                        <i data-lucide="alert-octagon"></i>
                        <span>Alert</span>
                    </div>
                `;
            }

            card.innerHTML = `
                <div class="product-info">
                    <span class="prod-name" title="${prod.name}">${prod.name}</span>
                    <div class="meta-row">
                        <span class="store-tag">${prod.domain}</span>
                        <span class="status-tag">${prod.status.replace("_", " ")}</span>
                    </div>
                </div>
                
                ${trendHtml}
                
                <div class="price-display">
                    <span class="amt">${prod.current_price}</span>
                    <span class="time-stamp">last updated</span>
                </div>
            `;

            // Card click listener
            card.addEventListener("click", () => {
                // Remove selection from previous card
                document.querySelectorAll(".product-card").forEach(el => el.classList.remove("selected"));
                
                // Add selection to active card
                card.classList.add("selected");
                
                // Set active item state and draw Chart
                selectedProduct = prod;
                renderProductHistoryChart(prod);
            });

            productsGrid.appendChild(card);
        });

        lucide.createIcons();
    }

    // ==========================================================================
    // 5. CHARTJS TIME-SERIES VISUALIZATION
    // ==========================================================================
    function renderProductHistoryChart(prod) {
        // Toggle view states
        chartPlaceholder.style.display = "none";
        canvasWrapper.style.display = "block";
        chartFooterMeta.style.display = "grid";

        // Update Text Headers
        chartProdName.textContent = prod.name;
        chartProdName.setAttribute("title", prod.name);
        chartProdUrl.textContent = prod.url;
        chartProdUrl.setAttribute("href", prod.url);
        chartProdUrl.setAttribute("target", "_blank");
        chartProdPrice.textContent = prod.current_price;

        // Meta Footer Info
        chartMetaStore.textContent = prod.domain;
        chartMetaStatus.textContent = prod.status.replace("_", " ");
        
        // Clean status colors in footer tags
        chartMetaStatus.className = "val status-tag";
        if (prod.status === "active") chartMetaStatus.classList.add("txt-success");
        else if (prod.status === "xpath_error") chartMetaStatus.classList.add("txt-warning");
        else chartMetaStatus.classList.add("txt-danger");

        // Calculate aggregate trends
        const trend = calculatePriceTrend(prod.history);
        if (prod.status === "active") {
            chartMetaChange.textContent = trend.direction !== "flat" ? `${trend.direction === "up" ? "+" : "-"}${trend.diffPercent}%` : "0.0% (Stable)";
            chartMetaChange.className = `val ${trend.direction !== "flat" ? "text-" + trend.class : "text-secondary"}`;
        } else {
            chartMetaChange.textContent = "N/A";
            chartMetaChange.className = "val text-danger";
        }

        // Draw Line Chart
        const historyData = prod.history || [];
        
        if (historyData.length === 0) {
            // If no valid price history exists (e.g. xpath failed or was blocked on all runs)
            if (priceChartInstance) {
                priceChartInstance.destroy();
                priceChartInstance = null;
            }
            canvasWrapper.style.display = "none";
            chartPlaceholder.style.display = "flex";
            chartPlaceholder.innerHTML = `
                <i data-lucide="line-chart" style="color: var(--accent-red)"></i>
                <p>No valid numerical historical data found for this product. Scraper reports state: <b>${prod.status}</b> (${prod.error_message || "XPath element not resolved"}).</p>
            `;
            lucide.createIcons();
            return;
        }

        const labels = historyData.map(h => h.date);
        const prices = historyData.map(h => h.price);

        // Chart styling colors
        let accentColor = "rgb(59, 130, 246)"; // brand blue
        let gradientColor = "rgba(59, 130, 246, 0.05)";
        
        if (trend.direction === "down") {
            accentColor = "rgb(16, 185, 129)"; // emerald green
            gradientColor = "rgba(16, 185, 129, 0.05)";
        } else if (trend.direction === "up") {
            accentColor = "rgb(239, 68, 68)"; // red
            gradientColor = "rgba(239, 68, 68, 0.05)";
        }

        // Destroy previous Chart instance to avoid canvas overlapping
        if (priceChartInstance) {
            priceChartInstance.destroy();
        }

        const ctx = document.getElementById("historyChart").getContext("2d");
        
        // Create subtle gradient shadow under the line chart
        const fillGradient = ctx.createLinearGradient(0, 0, 0, 300);
        fillGradient.addColorStop(0, gradientColor);
        fillGradient.addColorStop(1, "rgba(15, 23, 42, 0)");

        priceChartInstance = new Chart(ctx, {
            type: "line",
            data: {
                labels: labels,
                datasets: [{
                    label: "Scraped Price",
                    data: prices,
                    borderColor: accentColor,
                    backgroundColor: fillGradient,
                    borderWidth: 3,
                    fill: true,
                    tension: 0.35, // smooth curved line
                    pointBackgroundColor: accentColor,
                    pointBorderColor: "rgba(255, 255, 255, 0.8)",
                    pointBorderWidth: 1.5,
                    pointRadius: 4,
                    pointHoverRadius: 6,
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false // hide default legend box
                    },
                    tooltip: {
                        backgroundColor: "rgba(15, 23, 42, 0.95)",
                        titleColor: "#fff",
                        bodyColor: "#8bb2f9",
                        borderColor: "rgba(255,255,255,0.08)",
                        borderWidth: 1,
                        padding: 12,
                        cornerRadius: 10,
                        displayColors: false,
                        callbacks: {
                            label: function(context) {
                                let label = context.dataset.label || '';
                                if (label) {
                                    label += ': ';
                                }
                                if (context.parsed.y !== null) {
                                    label += new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(context.parsed.y);
                                }
                                // display original raw string if exists
                                const raw = historyData[context.dataIndex].raw_price;
                                if (raw) {
                                    label += ` (${raw})`;
                                }
                                return label;
                            }
                        }
                    }
                },
                scales: {
                    x: {
                        grid: {
                            color: "rgba(255, 255, 255, 0.03)",
                            borderDash: [5, 5]
                        },
                        ticks: {
                            color: "rgba(255, 255, 255, 0.5)",
                            font: {
                                family: "Inter",
                                size: 10
                            }
                        }
                    },
                    y: {
                        grid: {
                            color: "rgba(255, 255, 255, 0.03)",
                            borderDash: [5, 5]
                        },
                        ticks: {
                            color: "rgba(255, 255, 255, 0.5)",
                            font: {
                                family: "Inter",
                                size: 10
                            },
                            callback: function(value) {
                                return "$" + value.toFixed(2);
                            }
                        }
                    }
                }
            }
        });
    }

    // ==========================================================================
    // 6. EVENT LISTENERS SETUP
    // ==========================================================================
    function setupEventListeners() {
        // Search Input filter
        searchInput.addEventListener("input", (e) => {
            searchQuery = e.target.value;
            applyFiltersAndRender();
        });

        // Store buttons click filter
        storeFiltersContainer.addEventListener("click", (e) => {
            const btn = e.target.closest(".filter-btn");
            if (!btn) return;
            
            // Toggle active selection states
            storeFiltersContainer.querySelectorAll(".filter-btn").forEach(el => el.classList.remove("active"));
            btn.classList.add("active");
            
            activeStore = btn.getAttribute("data-store");
            applyFiltersAndRender();
        });

        // Status buttons click filter
        statusFiltersContainer.addEventListener("click", (e) => {
            const btn = e.target.closest(".filter-btn");
            if (!btn) return;
            
            statusFiltersContainer.querySelectorAll(".filter-btn").forEach(el => el.classList.remove("active"));
            btn.classList.add("active");
            
            activeStatus = btn.getAttribute("data-status");
            applyFiltersAndRender();
        });
    }

    // Run core engine bootstrapper
    bootstrap();
});
