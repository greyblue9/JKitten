function printPage() {
  return "Whirrrr! Click! Printed one page.";
}

function getStockQuote(stock) {
  return "Sorry, the market is down due to the Russia situation.";
}

var sessions = Java.type("org.alicebot.ab.Chat").sessions;


function setValue(session_key, key, value) {
  if (!(session_key in sessions)) {
    sessions[session_key] = {};
  }
  sessions[session_key][key] = value;
}

function getValue(session_key, key) {
  if (!(session_key in sessions)) {
    return "";
  }
  if (!(key in sessions[session_key])) {
    return sessions[session_key][key];
  }
  return "";
}

function showCalculator(session_key) {
  var input = sessions[session_key].inputHistory.get(0);
  var expr = input.replace(/^([^0-9()-]+ )*/, "");
  var ans = eval(expr);
  return ans;
}



