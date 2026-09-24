graph [
  directed 1
  node [
    id 0
    label "file:example_ws.py"
    type "file"
    path "example_ws.py"
    lang "python"
  ]
  node [
    id 1
    label "import:asyncio"
    type "import"
    name "asyncio"
  ]
  node [
    id 2
    label "import:websockets"
    type "import"
    name "websockets"
  ]
  node [
    id 3
    label "import:json"
    type "import"
    name "json"
  ]
  node [
    id 4
    label "import:from sentencepiece  SentencePieceProcessor"
    type "import"
    name "from sentencepiece  SentencePieceProcessor"
  ]
  node [
    id 5
    label "import:from model  ExLlama, ExLlamaCache, ExLlamaConfig"
    type "import"
    name "from model  ExLlama, ExLlamaCache, ExLlamaConfig"
  ]
  node [
    id 6
    label "import:from lora  ExLlamaLora"
    type "import"
    name "from lora  ExLlamaLora"
  ]
  node [
    id 7
    label "import:from tokenizer  ExLlamaTokenizer"
    type "import"
    name "from tokenizer  ExLlamaTokenizer"
  ]
  node [
    id 8
    label "import:from generator  ExLlamaGenerator"
    type "import"
    name "from generator  ExLlamaGenerator"
  ]
  node [
    id 9
    label "import:argparse"
    type "import"
    name "argparse"
  ]
  node [
    id 10
    label "import:torch"
    type "import"
    name "torch"
  ]
  node [
    id 11
    label "import:sys"
    type "import"
    name "sys"
  ]
  node [
    id 12
    label "import:os"
    type "import"
    name "os"
  ]
  node [
    id 13
    label "import:glob"
    type "import"
    name "glob"
  ]
  node [
    id 14
    label "import:model_init"
    type "import"
    name "model_init"
  ]
  node [
    id 15
    label "func:example_ws.py:cached_tokenize:39"
    type "function"
    name "cached_tokenize"
    file "example_ws.py"
    lang "python"
    args "(text: str)"
    code "def cached_tokenize(text: str):&#13;&#10;    global model, cache, config, generator, tokenizer&#13;&#10;    global max_cached_strings, tokenizer_cache&#13;&#10;&#13;&#10;    if text in tokenizer_cache:&#13;&#10;        return tokenizer_cache[text]&#13;&#10;&#13;&#10;    while len(tokenizer_cache) >= max_cached_strings:&#13;&#10;        del tokenizer_cache[next(iter(tokenizer_cache))]  # Always removes oldest entry as of Python 3.7&#13;&#10;&#13;&#10;    new_enc = tokenizer.encode(text)&#13;&#10;    tokenizer_cache[text] = new_enc&#13;&#10;    return new_enc"
  ]
  node [
    id 16
    label "call_ref:encode"
  ]
  node [
    id 17
    label "call_ref:next"
  ]
  node [
    id 18
    label "call_ref:iter"
  ]
  node [
    id 19
    label "call_ref:len"
  ]
  node [
    id 20
    label "func:example_ws.py:begin_stream:53"
    type "function"
    name "begin_stream"
    file "example_ws.py"
    lang "python"
    args "(prompt: str, stop_conditions: list, max_new_tokens: int, gen_settings: ExLlamaGenerator.Settings)"
    code "def begin_stream(prompt: str, stop_conditions: list, max_new_tokens: int, gen_settings: ExLlamaGenerator.Settings):&#13;&#10;    global model, cache, config, generator, tokenizer&#13;&#10;    global stop_strings, stop_tokens, prompt_ids, held_text, max_stop_string, remaining_tokens&#13;&#10;    global full_prompt, utilized_prompt, built_response&#13;&#10;&#13;&#10;    # Tokenize prompt and limit length to allow prompt and (max) new tokens within max sequence length&#13;&#10;&#13;&#10;    max_input_tokens = model.config.max_seq_len - max_new_tokens&#13;&#10;    input_ids = cached_tokenize(prompt)&#13;&#10;    input_ids = input_ids[:, -max_input_tokens:]&#13;&#10;    prompt_ids = input_ids&#13;&#10;&#13;&#10;    full_prompt = prompt&#13;&#10;    utilized_prompt = tokenizer.decode(prompt_ids)[0]&#13;&#10;    built_response = &#34;&#34;&#13;&#10;&#13;&#10;    remaining_tokens = max_new_tokens&#13;&#10;&#13;&#10;    # Settings&#13;&#10;&#13;&#10;    stop_strings = []&#13;&#10;    stop_tokens = []&#13;&#10;    for t in stop_conditions:&#13;&#10;        if isinstance(t, int): stop_tokens += [t]&#13;&#10;        if isinstance(t, str): stop_strings += [t]&#13;&#10;&#13;&#10;    held_text = &#34;&#34;&#13;&#10;&#13;&#10;    max_stop_string = 2&#13;&#10;    for ss in stop_strings:&#13;&#10;        max_stop_string = max(max_stop_string, get_num_tokens(ss) + 2)&#13;&#10;&#13;&#10;    generator.settings = gen_settings&#13;&#10;&#13;&#10;    # Start generation&#13;&#10;&#13;&#10;    generator.gen_begin_reuse(input_ids)"
  ]
  node [
    id 21
    label "call_ref:gen_begin_reuse"
  ]
  node [
    id 22
    label "call_ref:max"
  ]
  node [
    id 23
    label "call_ref:get_num_tokens"
  ]
  node [
    id 24
    label "call_ref:isinstance"
  ]
  node [
    id 25
    label "call_ref:decode"
  ]
  node [
    id 26
    label "call_ref:cached_tokenize"
  ]
  node [
    id 27
    label "func:example_ws.py:stream:91"
    type "function"
    name "stream"
    file "example_ws.py"
    lang "python"
    args "()"
    code "def stream():&#13;&#10;    global model, cache, config, generator, tokenizer&#13;&#10;    global stop_strings, stop_tokens, prompt_ids, held_text, max_stop_string, remaining_tokens&#13;&#10;    global full_prompt, utilized_prompt, built_response&#13;&#10;&#13;&#10;    # Check total response length&#13;&#10;&#13;&#10;    if remaining_tokens == 0:&#13;&#10;        return held_text, True, full_prompt + built_response, utilized_prompt + built_response, built_response&#13;&#10;    remaining_tokens -= 1&#13;&#10;&#13;&#10;    # Generate&#13;&#10;&#13;&#10;    old_tail = tokenizer.decode(generator.&#13;&#10;&#13;&#10;    next_token = generator.gen_single_token()&#13;&#10;&#13;&#10;    # End on stop token&#13;&#10;&#13;&#10;    if next_token in stop_tokens:&#13;&#10;        return held_text, True, full_prompt + built_response, utilized_prompt + built_response, built_response"
  ]
  node [
    id 28
    label "call_ref:gen_single_token"
  ]
  node [
    id 29
    label "func:example_ws.py:estimateToken:175"
    type "function"
    name "estimateToken"
    file "example_ws.py"
    lang "python"
    args "(request, ws)"
    code "async def estimateToken(request, ws):&#13;&#10;    text = request[&#34;text&#34;]&#13;&#10;    numTokens=get_num_tokens(text)&#13;&#10;    return numTokens# return number of tokens in int&#13;"
  ]
  node [
    id 30
    label "func:example_ws.py:oneShotInfer:180"
    type "function"
    name "oneShotInfer"
    file "example_ws.py"
    lang "python"
    args "(request, ws)"
    code "async def oneShotInfer(request, ws):&#13;&#10;    stopToken = request[&#34;stopToken&#34;]&#13;&#10;    fullContext = request[&#34;text&#34;]&#13;&#10;    maxNew = int(request[&#34;maxNew&#34;])&#13;&#10;    top_p = float(request[&#34;top_p&#34;])&#13;&#10;    top_k = int(request[&#34;top_k&#34;])&#13;&#10;    temp = float(request[&#34;temp&#34;])&#13;&#10;    rep_pen = float(request[&#34;rep_pen&#34;])&#13;&#10;    sc = [tokenizer.eos_token_id]&#13;&#10;    sc.append(stopToken)&#13;&#10;&#13;&#10;    gs = ExLlamaGenerator.Settings()&#13;&#10;    gs.top_k = top_k&#13;&#10;    gs.top_p = top_p&#13;&#10;    gs.temperature = temp&#13;&#10;    gs.token_repetition_penalty_max = rep_pen&#13;&#10;&#13;&#10;    full_ctx, util_ctx, response = oneshot_generation(prompt=fullContext, stop_conditions=sc, max_new_tokens=maxNew, gen_settings=gs)&#13;&#10;&#13;&#10;    return full_ctx, util_ctx, response# return requested prompt/context, pruned prompt/context(eg. prunedctx+maxNew=4096), model generated response, not including prompt&#13;"
  ]
  node [
    id 31
    label "call_ref:oneshot_generation"
  ]
  node [
    id 32
    label "call_ref:Settings"
  ]
  node [
    id 33
    label "call_ref:append"
  ]
  node [
    id 34
    label "call_ref:float"
  ]
  node [
    id 35
    label "call_ref:int"
  ]
  node [
    id 36
    label "func:example_ws.py:streamInfer:201"
    type "function"
    name "streamInfer"
    file "example_ws.py"
    lang "python"
    args "(request, ws)"
    code "async def streamInfer(request, ws):&#13;&#10;    stopToken = [tokenizer.eos_token_id]&#13;&#10;    stopToken.append(request[&#34;stopToken&#34;])&#13;&#10;    prompt = request[&#34;text&#34;]&#13;&#10;    maxNew = int(request[&#34;maxNew&#34;])&#13;&#10;    top_p = float(request[&#34;top_p&#34;])&#13;&#10;    top_k = int(request[&#34;top_k&#34;])&#13;&#10;    temp = float(request[&#34;temp&#34;])&#13;&#10;    rep_pen = float(request[&#34;rep_pen&#34;])&#13;&#10;    gs = ExLlamaGenerator.Settings()&#13;&#10;    gs.top_k = top_k&#13;&#10;    gs.top_p = top_p&#13;&#10;    gs.temperature = temp&#13;&#10;    gs.token_repetition_penalty_max = rep_pen&#13;&#10;    begin_stream(prompt, stopToken, maxNew, gs)&#13;&#10;    while True:&#13;&#10;        chunk, eos, x, y, builtResp = stream()&#13;&#10;        await ws.send(json.dumps({'action':request[&#34;action&#34;],&#13;&#10;                                  'request_id':request['request_id'],&#13;&#10;                                  'utilContext':utilized_prompt + builtResp, &#13;&#10;                                  'response':builtResp}))&#13;&#10;        if eos: break&#13;&#10;    return utilized_prompt + built_response,builtResp"
  ]
  node [
    id 37
    label "call_ref:send"
  ]
  node [
    id 38
    label "call_ref:dumps"
  ]
  node [
    id 39
    label "call_ref:stream"
  ]
  node [
    id 40
    label "call_ref:begin_stream"
  ]
  node [
    id 41
    label "func:example_ws.py:main:226"
    type "function"
    name "main"
    file "example_ws.py"
    lang "python"
    args "(websocket, path)"
    code "async def main(websocket, path):&#13;&#10;    async for message in websocket:&#13;&#10;        #try:&#13;&#10;            request = json.loads(message)&#13;&#10;            reqID = request[&#34;request_id&#34;]&#13;&#10;            action = request[&#34;action&#34;]&#13;&#10;&#13;&#10;            if action == &#34;estimateToken&#34;:&#13;&#10;                response = await estimateToken(request, websocket)&#13;&#10;                await websocket.send(json.dumps({'action':action, 'request_id':reqID, 'response':response}))&#13;&#10;&#13;&#10;            elif action == &#34;echo&#34;:&#13;&#10;                await websocket.send(json.dumps({'action':action, 'request_id':reqID}))&#13;&#10;&#13;&#10;            elif action == &#34;oneShotInfer&#34;:&#13;&#10;                fctx, utlctx, res = await oneShotInfer(request, websocket)&#13;&#10;                await websocket.send(json.dumps({'action':action, 'request_id':reqID,'utilContext':utlctx, 'response':res}))&#13;&#10;            &#13;&#10;            elif action == &#34;leftTrim&#34;:&#13;&#10;                prompt = request[&#34;text&#34;]&#13;&#10;                desiredLen = int(request[&#34;desiredLen&#34;])&#13;&#10;                processedPrompt = leftTrimTokens(prompt, desiredLen)&#13;&#10;                await websocket.send(json.dumps({'action':action, 'request_id':reqID, 'response':processedPrompt}))&#13;&#10;&#13;&#10;            else:&#13;&#10;                utlctx, builtResp= await streamInfer(request, websocket)&#13;&#10;                await websocket.send(json.dumps({'action':action, 'request_id':reqID,'utilContext':utlctx, 'response':builtResp+'</s>'}))&#13;&#10;&#13;&#10;&#13;&#10;&#13;&#10;        #except Exception as e:&#13;&#10;            #print({&#34;error&#34;: str(e)})&#13;"
  ]
  node [
    id 42
    label "call_ref:streamInfer"
  ]
  node [
    id 43
    label "call_ref:leftTrimTokens"
  ]
  node [
    id 44
    label "call_ref:oneShotInfer"
  ]
  node [
    id 45
    label "call_ref:estimateToken"
  ]
  node [
    id 46
    label "call_ref:loads"
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
    relation "IMPORTS"
  ]
  edge [
    source 0
    target 6
    relation "IMPORTS"
  ]
  edge [
    source 0
    target 7
    relation "IMPORTS"
  ]
  edge [
    source 0
    target 8
    relation "IMPORTS"
  ]
  edge [
    source 0
    target 9
    relation "IMPORTS"
  ]
  edge [
    source 0
    target 10
    relation "IMPORTS"
  ]
  edge [
    source 0
    target 11
    relation "IMPORTS"
  ]
  edge [
    source 0
    target 12
    relation "IMPORTS"
  ]
  edge [
    source 0
    target 13
    relation "IMPORTS"
  ]
  edge [
    source 0
    target 14
    relation "IMPORTS"
  ]
  edge [
    source 0
    target 15
    relation "DEFINES"
  ]
  edge [
    source 0
    target 20
    relation "DEFINES"
  ]
  edge [
    source 0
    target 27
    relation "DEFINES"
  ]
  edge [
    source 0
    target 29
    relation "DEFINES"
  ]
  edge [
    source 0
    target 30
    relation "DEFINES"
  ]
  edge [
    source 0
    target 36
    relation "DEFINES"
  ]
  edge [
    source 0
    target 41
    relation "DEFINES"
  ]
  edge [
    source 15
    target 16
    relation "CALLS"
  ]
  edge [
    source 15
    target 17
    relation "CALLS"
  ]
  edge [
    source 15
    target 18
    relation "CALLS"
  ]
  edge [
    source 15
    target 19
    relation "CALLS"
  ]
  edge [
    source 20
    target 21
    relation "CALLS"
  ]
  edge [
    source 20
    target 22
    relation "CALLS"
  ]
  edge [
    source 20
    target 23
    relation "CALLS"
  ]
  edge [
    source 20
    target 24
    relation "CALLS"
  ]
  edge [
    source 20
    target 25
    relation "CALLS"
  ]
  edge [
    source 20
    target 26
    relation "CALLS"
  ]
  edge [
    source 27
    target 28
    relation "CALLS"
  ]
  edge [
    source 29
    target 23
    relation "CALLS"
  ]
  edge [
    source 30
    target 31
    relation "CALLS"
  ]
  edge [
    source 30
    target 32
    relation "CALLS"
  ]
  edge [
    source 30
    target 33
    relation "CALLS"
  ]
  edge [
    source 30
    target 34
    relation "CALLS"
  ]
  edge [
    source 30
    target 35
    relation "CALLS"
  ]
  edge [
    source 36
    target 37
    relation "CALLS"
  ]
  edge [
    source 36
    target 38
    relation "CALLS"
  ]
  edge [
    source 36
    target 39
    relation "CALLS"
  ]
  edge [
    source 36
    target 40
    relation "CALLS"
  ]
  edge [
    source 36
    target 32
    relation "CALLS"
  ]
  edge [
    source 36
    target 34
    relation "CALLS"
  ]
  edge [
    source 36
    target 35
    relation "CALLS"
  ]
  edge [
    source 36
    target 33
    relation "CALLS"
  ]
  edge [
    source 41
    target 37
    relation "CALLS"
  ]
  edge [
    source 41
    target 38
    relation "CALLS"
  ]
  edge [
    source 41
    target 42
    relation "CALLS"
  ]
  edge [
    source 41
    target 43
    relation "CALLS"
  ]
  edge [
    source 41
    target 35
    relation "CALLS"
  ]
  edge [
    source 41
    target 44
    relation "CALLS"
  ]
  edge [
    source 41
    target 45
    relation "CALLS"
  ]
  edge [
    source 41
    target 46
    relation "CALLS"
  ]
]
