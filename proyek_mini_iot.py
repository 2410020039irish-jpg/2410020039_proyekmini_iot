import time
import random
import paho.mqtt.client as mqtt

# Konfigurasi Broker & Topik (NIM: 2410020039)
BROKER = "localhost"
PORT = 1883
NIM = "2410020039"

TOPIC_SUHU = f"iot/{NIM}/sensor/suhu"
TOPIC_RELAY = f"iot/{NIM}/aktuator/relay"
TOPIC_PWM = f"iot/{NIM}/aktuator/pwm"

# Status simulasi aktuator ESP32
status_relay = "OFF"
nilai_pwm = 0

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print(f"[MQTT] Terhubung ke broker ({BROKER}:{PORT})")
        client.subscribe(TOPIC_RELAY)
        client.subscribe(TOPIC_PWM)
        print(f"[SUB] Mendengarkan: {TOPIC_RELAY} & {TOPIC_PWM}\n")
    else:
        print(f"[MQTT] Gagal terhubung, kode error: {rc}")

def on_message(client, userdata, msg):
    global status_relay, nilai_pwm
    topik = msg.topic
    pesan = msg.payload.decode("utf-8")

    if topik == TOPIC_RELAY:
        status_relay = pesan
        kondisi = "MENYALA (HIGH)" if pesan == "ON" else "MATI (LOW)"
        print(f"---> [AKTUATOR RELAY GPIO 26] Status: {status_relay} -> {kondisi}")

    elif topik == TOPIC_PWM:
        try:
            nilai_pwm = int(float(pesan))
            persen = round((nilai_pwm / 255) * 100, 1)
            print(f"---> [AKTUATOR PWM GPIO 2] Duty Cycle: {nilai_pwm}/255 ({persen}%)")
        except ValueError:
            print(f"[WARNING] Nilai PWM tidak valid: {pesan}")

client = mqtt.Client(client_id=f"ESP32_Sim_{NIM}")
client.on_connect = on_connect
client.on_message = on_message

client.connect(BROKER, PORT, 60)
client.loop_start()

try:
    while True:
        suhu = round(random.uniform(24.0, 34.0), 1)
        client.publish(TOPIC_SUHU, str(suhu))
        print(f"[SENSOR DHT22] Publish {TOPIC_SUHU} = {suhu} °C | Relay: {status_relay} | PWM: {nilai_pwm}")
        time.sleep(3)
except KeyboardInterrupt:
    print("\n[SYSTEM] Simulasi dihentikan.")
    client.loop_stop()
    client.disconnect()