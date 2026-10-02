graph [
  directed 1
  node [
    id 0
    label "file:Main.java"
    type "file"
    path "Main.java"
    lang "java"
  ]
  node [
    id 1
    label "import:model.*"
    type "import"
    name "model.*"
  ]
  node [
    id 2
    label "import:strategy.*"
    type "import"
    name "strategy.*"
  ]
  node [
    id 3
    label "import:service.*"
    type "import"
    name "service.*"
  ]
  node [
    id 4
    label "import:exception.GatewayException"
    type "import"
    name "exception.GatewayException"
  ]
  node [
    id 5
    label "struct:Main.java:Main"
    type "class"
    name "Main"
    file "Main.java"
    lang "java"
    bases ""
  ]
  node [
    id 6
    label "func:Main.java:Main.main:7"
    type "method"
    name "main"
    file "Main.java"
    lang "java"
    args "(String[] args)"
    code "public static void main(String[] args) {&#13;&#10;        PaymentRequest request = new PaymentRequest(&#34;REQ_001&#34;, 100.0, Currency.USD);&#13;&#10;        PaymentProcessor processor = new PaymentProcessor(new CreditCardStrategy());&#13;&#10;&#13;&#10;        try {&#13;&#10;            processor.execute(request);&#13;&#10;        } catch (GatewayException e) {&#13;&#10;            System.err.println(&#34;L&#7895;i: &#34; + e.getMessage());&#13;&#10;        }&#13;&#10;    }"
  ]
  node [
    id 7
    label "call_ref:println"
  ]
  node [
    id 8
    label "call_ref:getMessage"
  ]
  node [
    id 9
    label "call_ref:execute"
  ]
  node [
    id 10
    label "file:exception\GatewayException.java"
    type "file"
    path "exception\GatewayException.java"
    lang "java"
  ]
  node [
    id 11
    label "struct:exception\GatewayException.java:GatewayException"
    type "class"
    name "GatewayException"
    file "exception\GatewayException.java"
    lang "java"
    bases "Exception"
  ]
  node [
    id 12
    label "class_ref:Exception"
  ]
  node [
    id 13
    label "func:exception\GatewayException.java:GatewayException.GatewayException:4"
    type "method"
    name "GatewayException"
    file "exception\GatewayException.java"
    lang "java"
    args "(String message)"
    code "public GatewayException(String message) {&#13;&#10;        super(message);&#13;&#10;    }"
  ]
  node [
    id 14
    label "file:model\Currency.java"
    type "file"
    path "model\Currency.java"
    lang "java"
  ]
  node [
    id 15
    label "struct:model\Currency.java:Currency"
    type "class"
    name "Currency"
    file "model\Currency.java"
    lang "java"
    bases ""
  ]
  node [
    id 16
    label "file:model\PaymentRequest.java"
    type "file"
    path "model\PaymentRequest.java"
    lang "java"
  ]
  node [
    id 17
    label "struct:model\PaymentRequest.java:PaymentRequest"
    type "class"
    name "PaymentRequest"
    file "model\PaymentRequest.java"
    lang "java"
    bases ""
  ]
  node [
    id 18
    label "func:model\PaymentRequest.java:PaymentRequest.PaymentRequest:8"
    type "method"
    name "PaymentRequest"
    file "model\PaymentRequest.java"
    lang "java"
    args "(String requestId, double amount, Currency currency)"
    code "public PaymentRequest(String requestId, double amount, Currency currency) {&#13;&#10;        this.requestId = requestId;&#13;&#10;        this.amount = amount;&#13;&#10;        this.currency = currency;&#13;&#10;    }"
  ]
  node [
    id 19
    label "func:model\PaymentRequest.java:PaymentRequest.getRequestId:14"
    type "method"
    name "getRequestId"
    file "model\PaymentRequest.java"
    lang "java"
    args "()"
    code "public String getRequestId() { return requestId; }"
  ]
  node [
    id 20
    label "func:model\PaymentRequest.java:PaymentRequest.getAmount:15"
    type "method"
    name "getAmount"
    file "model\PaymentRequest.java"
    lang "java"
    args "()"
    code "public double getAmount() { return amount; }"
  ]
  node [
    id 21
    label "func:model\PaymentRequest.java:PaymentRequest.getCurrency:16"
    type "method"
    name "getCurrency"
    file "model\PaymentRequest.java"
    lang "java"
    args "()"
    code "public Currency getCurrency() { return currency; }"
  ]
  node [
    id 22
    label "file:service\PaymentProcessor.java"
    type "file"
    path "service\PaymentProcessor.java"
    lang "java"
  ]
  node [
    id 23
    label "import:strategy.IPaymentStrategy"
    type "import"
    name "strategy.IPaymentStrategy"
  ]
  node [
    id 24
    label "import:model.PaymentRequest"
    type "import"
    name "model.PaymentRequest"
  ]
  node [
    id 25
    label "struct:service\PaymentProcessor.java:PaymentProcessor"
    type "class"
    name "PaymentProcessor"
    file "service\PaymentProcessor.java"
    lang "java"
    bases ""
  ]
  node [
    id 26
    label "func:service\PaymentProcessor.java:PaymentProcessor.PaymentProcessor:10"
    type "method"
    name "PaymentProcessor"
    file "service\PaymentProcessor.java"
    lang "java"
    args "(IPaymentStrategy strategy)"
    code "public PaymentProcessor(IPaymentStrategy strategy) {&#13;&#10;        this.strategy = strategy;&#13;&#10;    }"
  ]
  node [
    id 27
    label "func:service\PaymentProcessor.java:PaymentProcessor.setStrategy:14"
    type "method"
    name "setStrategy"
    file "service\PaymentProcessor.java"
    lang "java"
    args "(IPaymentStrategy strategy)"
    code "public void setStrategy(IPaymentStrategy strategy) {&#13;&#10;        this.strategy = strategy;&#13;&#10;    }"
  ]
  node [
    id 28
    label "func:service\PaymentProcessor.java:PaymentProcessor.execute:18"
    type "method"
    name "execute"
    file "service\PaymentProcessor.java"
    lang "java"
    args "(PaymentRequest request)"
    code "public boolean execute(PaymentRequest request) throws GatewayException {&#13;&#10;        return strategy.pay(request);&#13;&#10;    }"
  ]
  node [
    id 29
    label "call_ref:pay"
  ]
  node [
    id 30
    label "file:strategy\CreditCardStrategy.java"
    type "file"
    path "strategy\CreditCardStrategy.java"
    lang "java"
  ]
  node [
    id 31
    label "struct:strategy\CreditCardStrategy.java:CreditCardStrategy"
    type "class"
    name "CreditCardStrategy"
    file "strategy\CreditCardStrategy.java"
    lang "java"
    bases "IPaymentStrategy"
  ]
  node [
    id 32
    label "class_ref:IPaymentStrategy"
  ]
  node [
    id 33
    label "func:strategy\CreditCardStrategy.java:CreditCardStrategy.pay:7"
    type "method"
    name "pay"
    file "strategy\CreditCardStrategy.java"
    lang "java"
    args "(PaymentRequest request)"
    code "@Override&#13;&#10;    public boolean pay(PaymentRequest request) throws GatewayException {&#13;&#10;        if (request.getAmount() <= 0) {&#13;&#10;            throw new GatewayException(&#34;CreditCard: S&#7889; ti&#7873;n kh&#244;ng h&#7907;p l&#7879;&#34;);&#13;&#10;        }&#13;&#10;        System.out.println(&#34;Thanh to&#225;n CreditCard th&#224;nh c&#244;ng cho request &#34; + request.getRequestId());&#13;&#10;        return true;&#13;&#10;    }"
  ]
  node [
    id 34
    label "call_ref:getRequestId"
  ]
  node [
    id 35
    label "call_ref:getAmount"
  ]
  node [
    id 36
    label "file:strategy\IPaymentStrategy.java"
    type "file"
    path "strategy\IPaymentStrategy.java"
    lang "java"
  ]
  node [
    id 37
    label "struct:strategy\IPaymentStrategy.java:IPaymentStrategy"
    type "class"
    name "IPaymentStrategy"
    file "strategy\IPaymentStrategy.java"
    lang "java"
    bases ""
  ]
  node [
    id 38
    label "func:strategy\IPaymentStrategy.java:IPaymentStrategy.pay:7"
    type "method"
    name "pay"
    file "strategy\IPaymentStrategy.java"
    lang "java"
    args "(PaymentRequest request)"
    code "boolean pay(PaymentRequest request) throws GatewayException;"
  ]
  node [
    id 39
    label "file:strategy\PaypalStrategy.java"
    type "file"
    path "strategy\PaypalStrategy.java"
    lang "java"
  ]
  node [
    id 40
    label "struct:strategy\PaypalStrategy.java:PaypalStrategy"
    type "class"
    name "PaypalStrategy"
    file "strategy\PaypalStrategy.java"
    lang "java"
    bases "IPaymentStrategy"
  ]
  node [
    id 41
    label "func:strategy\PaypalStrategy.java:PaypalStrategy.pay:7"
    type "method"
    name "pay"
    file "strategy\PaypalStrategy.java"
    lang "java"
    args "(PaymentRequest request)"
    code "@Override&#13;&#10;    public boolean pay(PaymentRequest request) throws GatewayException {&#13;&#10;        if (request.getAmount() <= 0) {&#13;&#10;            throw new GatewayException(&#34;Paypal: S&#7889; ti&#7873;n kh&#244;ng h&#7907;p l&#7879;&#34;);&#13;&#10;        }&#13;&#10;        System.out.println(&#34;Thanh to&#225;n Paypal th&#224;nh c&#244;ng cho request &#34; + request.getRequestId());&#13;&#10;        return true;&#13;&#10;    }"
  ]
  edge [
    source 0
    target 1
    relation "IMPORTS"
  ]
  edge [
    source 0
    target 2
    relation "IMPORTS"
  ]
  edge [
    source 0
    target 3
    relation "IMPORTS"
  ]
  edge [
    source 0
    target 4
    relation "IMPORTS"
  ]
  edge [
    source 0
    target 5
    relation "DEFINES"
  ]
  edge [
    source 0
    target 6
    relation "DEFINES"
  ]
  edge [
    source 5
    target 6
    relation "HAS_METHOD"
  ]
  edge [
    source 6
    target 7
    relation "CALLS"
  ]
  edge [
    source 6
    target 8
    relation "CALLS"
  ]
  edge [
    source 6
    target 9
    relation "CALLS"
  ]
  edge [
    source 10
    target 11
    relation "DEFINES"
  ]
  edge [
    source 10
    target 13
    relation "DEFINES"
  ]
  edge [
    source 11
    target 12
    relation "INHERITS"
  ]
  edge [
    source 11
    target 13
    relation "HAS_METHOD"
  ]
  edge [
    source 14
    target 15
    relation "DEFINES"
  ]
  edge [
    source 16
    target 17
    relation "DEFINES"
  ]
  edge [
    source 16
    target 18
    relation "DEFINES"
  ]
  edge [
    source 16
    target 19
    relation "DEFINES"
  ]
  edge [
    source 16
    target 20
    relation "DEFINES"
  ]
  edge [
    source 16
    target 21
    relation "DEFINES"
  ]
  edge [
    source 17
    target 18
    relation "HAS_METHOD"
  ]
  edge [
    source 17
    target 19
    relation "HAS_METHOD"
  ]
  edge [
    source 17
    target 20
    relation "HAS_METHOD"
  ]
  edge [
    source 17
    target 21
    relation "HAS_METHOD"
  ]
  edge [
    source 22
    target 23
    relation "IMPORTS"
  ]
  edge [
    source 22
    target 24
    relation "IMPORTS"
  ]
  edge [
    source 22
    target 4
    relation "IMPORTS"
  ]
  edge [
    source 22
    target 25
    relation "DEFINES"
  ]
  edge [
    source 22
    target 26
    relation "DEFINES"
  ]
  edge [
    source 22
    target 27
    relation "DEFINES"
  ]
  edge [
    source 22
    target 28
    relation "DEFINES"
  ]
  edge [
    source 25
    target 26
    relation "HAS_METHOD"
  ]
  edge [
    source 25
    target 27
    relation "HAS_METHOD"
  ]
  edge [
    source 25
    target 28
    relation "HAS_METHOD"
  ]
  edge [
    source 28
    target 29
    relation "CALLS"
  ]
  edge [
    source 30
    target 24
    relation "IMPORTS"
  ]
  edge [
    source 30
    target 4
    relation "IMPORTS"
  ]
  edge [
    source 30
    target 31
    relation "DEFINES"
  ]
  edge [
    source 30
    target 33
    relation "DEFINES"
  ]
  edge [
    source 31
    target 32
    relation "INHERITS"
  ]
  edge [
    source 31
    target 33
    relation "HAS_METHOD"
  ]
  edge [
    source 33
    target 7
    relation "CALLS"
  ]
  edge [
    source 33
    target 34
    relation "CALLS"
  ]
  edge [
    source 33
    target 35
    relation "CALLS"
  ]
  edge [
    source 36
    target 24
    relation "IMPORTS"
  ]
  edge [
    source 36
    target 4
    relation "IMPORTS"
  ]
  edge [
    source 36
    target 37
    relation "DEFINES"
  ]
  edge [
    source 36
    target 38
    relation "DEFINES"
  ]
  edge [
    source 37
    target 38
    relation "HAS_METHOD"
  ]
  edge [
    source 39
    target 24
    relation "IMPORTS"
  ]
  edge [
    source 39
    target 4
    relation "IMPORTS"
  ]
  edge [
    source 39
    target 40
    relation "DEFINES"
  ]
  edge [
    source 39
    target 41
    relation "DEFINES"
  ]
  edge [
    source 40
    target 32
    relation "INHERITS"
  ]
  edge [
    source 40
    target 41
    relation "HAS_METHOD"
  ]
  edge [
    source 41
    target 7
    relation "CALLS"
  ]
  edge [
    source 41
    target 34
    relation "CALLS"
  ]
  edge [
    source 41
    target 35
    relation "CALLS"
  ]
]
