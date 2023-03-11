<script>
    let messages = ['loading...'];
    import { onMount } from 'svelte';
    import store from '../store.js';
    let current = 1;
    onMount(() => {
        store.subscribe(async currentMessage => {
            messages = [...messages, currentMessage];
            current = 1*currentMessage
        })});
    let files = ['sahaj1.png','devday.png', 'sahaj.png'];
</script>
<img src="{files[current%3]}" alt="devday" width="100%" height="100%">

<pre>
    {messages}
</pre>