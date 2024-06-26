
def safe_logging(msg):
    with log_lock:
        logging.info(msg)


@app.route("/predict", methods=["POST"])
def predict():
    ip_address = request.remote_addr

    data = request.get_json()
    url = data["url"]

    parser = URLParser(url)

    prediction = model.predict(parser.np_array())

    output = prediction[0].item()  # Convert numpy integer to Python integer

    # Add an entry
    result = "safe" if output == 0 else "phishing"
    store_thread = threading.Thread(
        target=add_entry,
        args=(
            ip_address,
            datetime.datetime.now(),
            url,
            result,
        ),
    )
    store_thread.start()

    # Log the prediction
    safe_logging(
        f"Prediction for {url}: {'phishing' if output == 1 else 'safe browsing'}"
    )

    return jsonify(
        {
            "prediction": output,
            "url": url,
            "message": (
                "Prediction says it's a phishing URL"
                if output == 1
                else "Prediction says it's a safe browsing URL"
            ),
        }
    )


@app.route("/fetch", methods=["GET"])
def fetch():
    all_entries = fetch_all_entries()
    for entry in all_entries:
        safe_logging(f"Fetched entry: {entry}")

    return jsonify(all_entries)


@app.route("/history", methods=["GET"])
def fetchui():
    all_entries = fetch_all_entries()

    return render_template("history.html", history=all_entries)


@app.route("/", methods=["POST", "GET"])
def predictui():
    if request.method == "GET":
        return render_template("index.html", prediction="", url=None)
    elif request.method == "POST":
        url = request.form["url"]
        try:
            ip_address = request.remote_addr

            parser = URLParser(url)

            prediction = model.predict(parser.np_array())

            output = prediction[0].item()  # Convert numpy integer to Python integer

            # Add an entry
            result = "safe" if output == 0 else "phishing"
            store_thread = threading.Thread(
                target=add_entry,
                args=(
                    ip_address,
                    datetime.datetime.now(),
                    url,
                    result,
                ),
            )
            store_thread.start()

            # Log the prediction
            safe_logging(
                f"Prediction for {url}: {'phishing' if output == 1 else 'safe browsing'}"
            )

            message = (
                "Prediction says phishing URL"
                if output == 1
                else "Prediction says safe browsing URL"
            )
            return render_template("index.html", prediction=message, url=url)
        except Exception as e:
            safe_logging(f"An error occurred: {str(e)}")
            return render_template("index.html", prediction="broken url", url=url)





if __name__ == "__main__":
    app.run(port=5000, debug=True)
