Eos = require("eosjs"); // Eos = require('./src')

wif = "5JhhMGNPsuU42XXjZ57FcDKvbb7KLrehN65tdTQFrH51uruZLHi";
pubkey = "EOS7ckzf4BMgxjgNSYV22rtTXga8R9Z4XWVhYp8TBgnBi2cErJ2hn";

eos = Eos({ keyProvider: wif, httpEndpoint: "http://localhost:8888", verbose: true, broadcast : false });

eos.transaction({
  actions: [
    {
      account: "gh",
      name: "newscan",
      authorization: [
        {
          actor: "gh",
          permission: "active"
        },
        {
          actor: "gh",
          permission: "active"
        }
      ],
      data: {
        _serial: "12345",
        _sku : "CCZ-20oz",
        _latlon: "New York, NY", 
        _imagehash : "QmSqcJwsXMivki9q52qkYun3iXjPPvnLyv1jh9tfZdko7U"
      }
    }
  ]
});
