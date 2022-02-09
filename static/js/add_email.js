function add_email(){
  fetch("/add_email", {
    method: "POST",
    headers: {
      'Accept': 'application/json',
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({email: document.getElementById("Newsletter-Email").value})

  }).then(res => res.json())
    .then(data => {
      document.getElementById("error_message").innerHTML = data.returns;
    }).catch(err => {
      console.log(err);
      document.getElementById("error_message").innerHTML = "Problem Saving email"
    })
}