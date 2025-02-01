function dashboard() {
    return {
        stats: {
            total_banks: 0,
            processed_banks: 0,
            completion_percentage: 0
        },
        urlStatus : {
            is_running: false,
            total_countries: 0,
            processed_countries: 0,
            current_country: '',
            collected_urls: 0,
            failed_countries: []
        },
        scrapingStatus: {
            is_running: false,
            resumable: false,
            total_banks: 0,
            processed_banks: 0,
            processed_bins: 0,
            current_bank: '',
            completion_percentage: 0,
            failed_urls: [],
            start_time: null,
            last_update: null,
            rate: '0',
            eta: 'Calculating...'
        },
        search: {
            bin: '',
            bank: '',
            country: ''
        },
        searchResults: [],
        pollingInterval: null,
        
        init() {
            this.checkResumable();
            this.startPolling();
        },

        cleanup() {
            if (this.pollingInterval) {
                clearInterval(this.pollingInterval);
                this.pollingInterval = null;
            }
        },

        async checkResumable() {
            try {
                const response = await fetch('/api/scraping/resumable');
                const data = await response.json();
                
                // Update individual properties to maintain reactivity
                this.scrapingStatus.resumable = data.resumable;
                this.scrapingStatus.total_banks = data.total;
                this.scrapingStatus.processed_banks = data.processed;
            } catch (error) {
                console.error('Error checking resumable status:', error);
                this.scrapingStatus.resumable = false;
            }
        },
        
        updateScrapingStatus(progress) {
            // Update each property individually
            Object.assign(this.scrapingStatus, progress, {
                rate: this.calculateRate(progress),
                eta: this.calculateETA(progress)
            });
        },

        startPolling() {
            this.fetchUpdates();
            this.pollingInterval = setInterval(() => {
                this.fetchUpdates();
            }, 1000);
        },

        async fetchUpdates() {
            try {
                const [statsResponse, urlStatusResponse, scrapingProgressResponse] = await Promise.all([
                    fetch('/api/stats'),
                    fetch('/api/urls/status'),
                    fetch('/api/scraping/progress')
                ]);
                
                this.stats = await statsResponse.json();
                const newUrlStatus = await urlStatusResponse.json();
                const scrapingProgress = await scrapingProgressResponse.json();
                
                // Update URL collection status
                Object.keys(this.urlStatus).forEach(key => {
                    if (key in newUrlStatus) {
                        this.urlStatus[key] = newUrlStatus[key];
                    }
                });

                // Update scraping status
                this.updateScrapingStatus(scrapingProgress);

                // Stop polling if both processes are inactive
                if (!this.urlStatus.is_running && !this.scrapingStatus.is_running) {
                    clearInterval(this.pollingInterval);
                }
            } catch (error) {
                console.error('Error fetching updates:', error);
            }
        },

        async toggleUrlCollection() {
            const endpoint = this.urlStatus.is_running ? 
                '/api/urls/collect/stop' : '/api/urls/collect/start';
            
            try {
                await fetch(endpoint, { method: 'POST' });
                if (!this.pollingInterval) this.startPolling();
                await this.fetchUpdates();
            } catch (error) {
                console.error('Error toggling collection:', error);
            }
        },        

        calculateRate(progress) {
            if (!progress.start_time || !progress.processed_banks) return '0';
            const elapsed = (new Date() - new Date(progress.start_time)) / 1000 / 60; // minutes
            return (progress.processed_banks / elapsed).toFixed(1);
        },

        calculateETA(progress) {
            if (!progress.start_time || !progress.processed_banks) return 'Calculating...';
            const elapsed = (new Date() - new Date(progress.start_time)) / 1000; // seconds
            const rate = progress.processed_banks / elapsed;
            if (rate === 0) return 'Calculating...';
            
            const remaining = progress.total_banks - progress.processed_banks;
            const eta = remaining / rate;
            return this.formatTime(eta);
        },

        formatTime(seconds) {
            if (seconds < 60) return Math.round(seconds) + 's';
            if (seconds < 3600) return Math.round(seconds / 60) + 'm';
            return Math.round(seconds / 3600) + 'h';
        },

        async startScraping(resume = false) {
            try {
                await fetch('/api/scraping/start', { 
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ resume })
                });
                if (!this.pollingInterval) this.startPolling();
                await this.fetchUpdates();
            } catch (error) {
                console.error('Error starting scraping:', error);
            }
        },

        async toggleScraping() {
            if (this.scrapingStatus.is_running) {
                await fetch('/api/scraping/stop', { method: 'POST' });
            } else {
                await this.startScraping();
            }
            await this.fetchUpdates();
        },

        async performSearch() {
            const params = new URLSearchParams({
                ...(this.search.bin && { bin_prefix: this.search.bin }),
                ...(this.search.bank && { bank: this.search.bank }),
                ...(this.search.country && { country: this.search.country })
            });
            
            const response = await fetch(`/api/search?${params}`);
            this.searchResults = await response.json();
        },

        formatPercentage(value) {
            return Number(value).toFixed(1);
        },
    }
}
