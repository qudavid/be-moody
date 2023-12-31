import React from 'react';
import axios from 'axios';

import useStyles from './styles';

const FileUpload = () => {
  const classes = useStyles();

  const handleFileUpload = (event) => {
    // get the selected file from the input
    const file = event.target.files[0];
    // create a new FormData object and append the file to it
    const formData = new FormData();
    formData.append('file', file);

    axios
      .post('http://127.0.0.1:5000//upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      })
      .then((response) => {
        // handle the response
        console.log(response);
      })
      .catch((error) => {
        // handle errors
        console.log(error);
      });
  };
  // render a simple input element with an onChange event listener that calls the handleFileUpload function
  return (
    <>
      <div className={classes.fileCard}>
        <div className={classes.fileInputs}>
          <input className={classes.input} type="file" onChange={handleFileUpload} />
        </div>
      </div>
    </>
  );
};
export default FileUpload;
