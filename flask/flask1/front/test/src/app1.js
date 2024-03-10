import React, { useState, useEffect } from 'react';
import axios from 'axios';



const App = () => {
  const [data, setData] = useState([]);
  const [plot, setPlot] = useState([]); 
  const [loading, setLoading] = useState(true);
  const [name, setName] = useState([]); 

  useEffect(() => {
    axios.get('/data')
    .then(response => {
        setData(response.data.data);
        setLoading(false);
      })
      .catch(err => {
        setLoading(false);
      });

    axios.get('/plot')
    .then(response => {
        setPlot(response.data.plot);
        setLoading(false);
         console.log( plot ) ; 
      })
      .catch(err => {
        setLoading(false);
      });



  }, []);

  if (loading) {
    return <div>Loading...</div>;
  }

  return (

<body>


<div>
  <p> test :  {data[0].name} {data[0].age }  </p>
<figure>
  <img
//    src="https://raw.githubusercontent.com/mdn/learning-area/master/html/multimedia-and-embedding/images-in-html/dinosaur_small.jpg"
    src = {`data:image/png;base64,${plot}`}
    alt="一只恐龙头部和躯干的骨架，它有一个巨大的头，长着锋利的牙齿。"
   // width="400"
   // height="341" 
  />
  <figcaption>曼彻斯特大学博物馆展出的一只霸王龙的化石</figcaption>
</figure>
</div>

//<div>
//<input type="text" id="name" name="name" required minlength="4" maxlength="8" size="10" />
//</div>

<div>
<form>
      <label>Enter your name:
        <input
          type="text" 
          value={name}
          onChange={(e) => setName(e.target.value)}
        />
      </label>
    </form>
</div>

<div>
<form>
      <div>
        <label htmlFor="email">Email</label>
        <input id="email" type="text" />
      </div>
      <div>
        <label htmlFor="password">Password</label>
        <input id="password" type="password" />
      </div>
      <button>Submit</button>
    </form>

</div>


</body>

);
};

export default App;
