An exporter about prometheus, written in Python, mainly provides monitoring of api data functions, as follows:
     1. Request quantity
     2. Request duration per second
     3. The number being requested
     4. The last request took time

For details, please see: https://github.com/prometheus/client_python

Usage example:
    """
    
    from apimon import ApiMonitor

    apimonitor = ApiMonitor(app_name="your app name")
    apimonitor.setup_metrics(app)  # your app object instance
    
    """
