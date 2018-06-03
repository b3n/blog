site:
	./makesite.py

serve: site
	cd _site && python -m SimpleHTTPServer 2> /dev/null || python3 -m http.server

clean:
	find . -name "__pycache__" -exec rm -r {} +
	find . -name "*.pyc" -exec rm {} +
