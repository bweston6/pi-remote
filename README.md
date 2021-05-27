# Raspberry Pi IR Transmitter Web Interface
This project uses Python's `Flask` to host a TV-remote web interface, which uses `ir-ctl` to emit remote codes from an infrared LED.

All that means that you can use any device on the local network as a remote control for your TV, or other IR device. 

## Hardware

* [Raspberry Pi 3B](https://www.raspberrypi.org/products/raspberry-pi-3-model-b/)
	* Located by the TV for best reception.
* [iHaospace IR Transmitter Shield](https://www.amazon.co.uk/dp/B089RD8138)
	* Any GPIO based transmitter should work - just take note of the pins that the LEDs are connected to.

## Installation
To complete this installation I used [Pi OS Lite](https://downloads.raspberrypi.org/raspios_lite_armhf/images/raspios_lite_armhf-2021-03-25/2021-03-04-raspios-buster-armhf-lite.zip) (Mach 4th 2021). I will presume you already have this flashed to an SD card and have WiFi and SSH setup:

1. Uncomment the following lines in `/boot/config.txt` replacing the first with your IR receiver pin and the second with your IR transmitter pin:

	```ini
	# Uncomment this to enable infrared communication.
	dtoverlay=gpio-ir,gpio_pin=18
	dtoverlay=gpio-ir-tx,gpio_pin=17
	```
	
	* My pins are 18 for receive and 17 for send. 
	* You don't need to have a receiver but it will help if you need [register your own keys](#receiving-key-codes-and-customisation).

1. To run the Flask server, and interface with the GPIO, you will have to install some Python packages.

	`ir-keytable` will allow you to test that receiving is working, and record the key-codes with their protocol emitted from your remote.

	This is also a good time to update the Pi:

	```shell
	$ sudo apt update
	$ sudo apt full-upgrade python3-flask python3-waitress python3-rpi.gpio ir-keytable
	```
	
	You should reboot after this step so that the kernel overlays from the previous step, and the updates, are loaded.
	
1. From here you can look at customisation, or start the server by running `sudo ./server.py` at the root of the repository:

	* This will start the server on port 80, so you just need to point a web browser to the Pi's host-name or IP address.
	
	* The codes emitted are, by default, for a [JVC LT40C550](https://business.currys.co.uk/catalogue/tv-entertainment/tvs/32-42-inch-tvs/jvc-lt-40c550-40-led-tv/B127240B); so this likely won't work with your TV out of the box. There are also two more remotes for RGB lights.
	
1. To start the web server at boot, you can make a `systemd` service to start it for you. Make the following file as root: `/etc/systemd/system/webRemote.service`, with the following content:

	```
	[Unit]
	Description=An IR remote webserver.
	After=network-online.target

	[Service]
	ExecStart=/home/pi/webRemote/server.py

	[Install]
	WantedBy=multi-user.target
	```
	
	To notify `systemd` of the new service, enable and start it run the following:
	
	```shell
	$ sudo systemctl daemon-reload
	$ sudo systemctl enable --now webRemote.service
	```
	
	* This will start the server on port 80, so you just need to point a web browser to the Pi's host-name or IP address.


## Receiving Key-Codes and Customisation
### Receiving
This code works great if you have a JVC LT40C550 TV, or similar RGB lights, but you probably don't. To test that your receiver is working and to note the codes and protocol run the following:

```shell
$ sudo ir-keytable -t -p all
```

Point your remote as the receiver and start mashing some buttons:

* If you get output, and there were no errors when running the command, then you're good to start noting down all the buttons.
* If not refer to `ir-keytable --help` as you may need to manually specify your device with `--device` or `--sysdev`.

### Manually Transmitting
To manually send a key-code refer to the output of `ir-keytable` and take note of the protocol and the key value.

To transmit this information, use the following command:

```shell
$ sudo ir-ctl -S nec:0xa1f -d /dev/lirc0
```

* `nec` is the protocol.
* `0xa1f` is the key-code.
* `/dev/lirc0` is the device name of the transmitter.

Your TV should respond, and you might be able to see the IR LED flash by looking through the viewfinder of a phone camera.

### Recording Key-Codes
The `keyCodes` and `keyNames` are recorded in `irBlaster.py`:

* Note your remote's protocol as you will have to pass it to the `blast(keyName, protocol)` function in `server.py`.
* Study the format of the key names in `__decode(keyName)` and enter your own values.
	
	The variable names themselves don't matter, but you will call them later via the webpage. Ensure that they are assigned as strings and not as hex like in the file.
	
### Modifying the TV-Remote Webpage
There is no super simple way of making your own TV-remote page but it is pretty easy to get a hang of how flask works and replace the buttons with your own.

Start by looking at `server.py`:

* The `@app.route()` is the URL that the code refers to.
	* Values in `<>` can be taken from the URL as an argument.
* The `return` value is the webpage that is returned when a particular link is followed.
* Any code in-between is python code, such as the `blast(keyName, protocol)` function, that you want to run.

In the `templates/` directory are the webpages that `server.py` can refer to. You can see from `templates/index.html` how the Python code is called:

* Each button is located within a table and has the following attributes:
	* `href` - This is generally blank (`#`) as JavaScript/jQuery is used to handle the non-redirecting buttons.
	* `id` - This is the `keyName` from `ir-Blaster` that you want to send. The `/query/...` is called by `jQuery`.
	* `class` - There are some styles at the top that you can apply so the buttons have rounded edges. This helps with grouping.
	* In-between the `<a...> </a>` tags is the text that you want to appear on the buttons. I'm using [font-awesome](https://fontawesome.com/) icons for most of these. Please make your own account as mine is only free so there are limits.
* For examples of buttons that redirect, look for `KEY_SUBTITLE`, `KEY_AUDIO` and so on in `templates/extra.html`. These don't have `id`s so that they won't be caught by the JavaScript and link to `/redirect/<keyName>`.
	* Buttons that don't change the page shouldn't be done like this so that the page doesn't refresh in-between each button press.
* Ensure that the matching statement in the JavaScript correctly matches the start of your key-names. For example, in `index.html`, `[id^=KEY]` matches IDs (`id`) that start with (`^=`) `KEY`.
