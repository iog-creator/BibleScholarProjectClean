if __name__ == '__main__':
    import os
    import sys
    port = int(os.getenv('PORT', 5000))
    debug = '--debug' in sys.argv
    app.run(debug=debug, port=port) 