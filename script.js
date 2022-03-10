function printPage() {
  return "Whirrrr! Click! Printed one page.";
}

function getStockQuote(stock) {
  return "Sorry, the market is down due to the Russia situation.";
}

var knowledge = {};


function setValue(session_key, key, value) {
  if (!(session_key in knowledge)) {
    knowledge[session_key] = {};
  }
  knowledge[session_key][key] = value;
}

function getValue(session_key, key) {
  if (!(session_key in knowledge)) {
    return "something I don't know";
  }
  if (!(key in knowledge[session_key])) {
    return knowledge[session_key][key];
  }
  return "something you haven't told me yet";
}

