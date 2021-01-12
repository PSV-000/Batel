const transactionHeaders = ["Card Name", "Set Name", "Edition", "Condition", "Basis Price", "Quantity", "Transaction Type"];
const inventoryHeaders = ["Card Name", "Set Name", "Rarity", "Edition", "Condition", "Price", "Quantity"];
const saleHeaders = ["Card Name", "Set Name", "Rarity", "Edition", "Condition", "Basis Price", "Sale Price", "Quantity", "MOIC", "MOIC %", "IRR"];
transactionHeaders.forEach((item) => inputTableHeaders("transactionHeader", item));
inventoryHeaders.forEach((item) => inputTableHeaders("inventoryHeader", item));
saleHeaders.forEach((item) => inputTableHeaders("saleHeader", item));

const transactionInputs = ["cardName", "setName", "edition", "condition", "price", "quantity"];
transactionInputs.forEach((item) => inputNewTransactions("transactionInput", item));
const transactionInputTypes = [["buy", "BUY"],["sell", "SELL"],["tradein", "TRADE IN"],["tradeout", "TRADE OUT"]];
//document.getElementById("transactionInput").innerHTML += "<td>"
transactionInputTypes.forEach((item) => inputTransactionTypes("transactionInput", item));
//document.getElementById("transactionInput").innerHTML += "</td>"


// Functions

function inputTableHeaders(id, item) {
    document.getElementById(id).innerHTML += "<th>" + item + "</th>";
}
function inputNewTransactions(id, item) {
    document.getElementById(id).innerHTML += '<td><input name=' + item + ' type="text"></td>';
}
function inputTransactionTypes(id, item) {
    document.getElementById(id).innerHTML += '<label for=' + item[0] + '>' + item[1] + '</label><input name="type" type="radio">'
}

function revealMessage() {
    if(document.getElementById("hiddenMessage").style.display === "none") {
        document.getElementById("hiddenMessage").style.display = "block";
    } else {
        document.getElementById("hiddenMessage").style.display = "none";
    }
}
