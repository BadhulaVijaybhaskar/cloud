const express = require('express');
const app = express();
app.get('/health', (req,res)=>res.json({status:"healthy",component:"pricing-console"}));
app.get('/', (req,res)=>res.send('<html><body><h1>Pricing Console (Simulation)</h1><p>LaunchPad theme reuse planned.</p></body></html>'));
app.listen(process.env.PORT || 8310, ()=>console.log('pricing-console up'));