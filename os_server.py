"""Start the AnshuX OS local control plane."""

from anshux_os.api import create_app


app = create_app()


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8765, debug=False)
