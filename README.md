# Advanced SQL Injection Scanner v4.0

🔍 A powerful tool for scanning SQL Injection vulnerabilities using GET and POST methods, with automatic proxy support.

---

## 🛠️ Requirements

- Python 3.7 or higher
- `requests` library
- `colorama` library

Install the required libraries by running:
```bash
pip install requests colorama
```

---

## 🚀 How to Run

1. Make sure Python is installed on your system.

2. Open a terminal (or command prompt) and navigate to the script's directory:
```bash
cd path/to/your/folder
```

3. Run the script:
```bash
python your_script_name.py
```
Example:
```bash
python scanner.py
```

---

## 📝 How to Use

When you launch the script:

1. It will automatically fetch a list of free proxies.

2. It will prompt you to **enter the full URL** you want to scan, e.g.:
   ```
   https://example.com/item.php?id=
   ```

3. Choose the **HTTP method**:
   - `GET`
   - `POST`

4. If you choose `POST`, it will ask for POST data like:
   ```
   id=1
   ```

5. The scanner will start testing the URL with various SQL injection payloads and also check for **Blind SQL Injection** vulnerabilities.

6. All the scan results will be saved automatically inside a file called `log.txt`.

---

## 📋 Features

- Traditional SQLi payload testing.
- Blind SQL Injection detection using time delays.
- Random proxy usage for anonymity.
- Supports both GET and POST methods.
- Auto-saving scan results into a log file.

---

## ⚠️ Legal Warning

❗ This tool is intended for educational purposes and authorized security testing only.  
❗ The user is solely responsible for any misuse or illegal activities.

---

## ✨ Example Usage

```bash
python scanner.py
```
- Enter URL:  
  `https://testphp.vulnweb.com/listproducts.php?cat=`

- Choose method:  
  `GET`

- The scan will run, showing results in the terminal and saving them to `log.txt`.

---

## 👨‍💻 Author

- Written in Python.
- Script Version: v4.0
