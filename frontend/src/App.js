import React, { useState } from "react";
import {
  FormControl,
  InputLabel,
  Input,
  FormHelperText,
  Button,
  LinearProgress,
} from "@material-ui/core";
import { CSVLink, CSVDownload } from "react-csv";
import { DataGrid } from "@material-ui/data-grid";
import "./App.css";

function App() {
  const [inputURL, setInputURL] = useState("");
  const [rows, setRows] = useState([]);
  const [rowSelection, setRowSelection] = useState([]);
  const [columns, setColumns] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [csvData, setCSVData] = useState(null);

  const inputHandler = (event) => {
    setInputURL(event.target.value);
  };

  const getPIIHandler = (event) => {
    event.preventDefault();

    setLoading(true);
    setError(null);

    const requestOptions = {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ url: inputURL }),
    };

    fetch("/get_pii", requestOptions)
      .then((response) => response.json())
      .then((data) => {
        setLoading(false);
        const tempCols = data["columns"].map((c) => {
          return {
            field: c,
            headerName: c,
            width: 150,
            editable: false,
          };
        });
        setColumns(tempCols);
        const tempRows = data["rowData"].map((row, id) => {
          return { id: id, ...row };
        });
        console.log(tempRows);
        setRows(tempRows);
      })
      .catch((error) => {
        setLoading(false);
        setError(error);
        console.error("There was an error!", error);
      });
    setInputURL("");
  };

  const downloadCSVHandler = () => {
    let downloadData = null;
    if (rowSelection.length === 0) downloadData = rows;
    else downloadData = rowSelection.map((id) => rows[id]);
    console.log(downloadData);
    setCSVData(downloadData);
  };

  let table = <></>;
  if (rows.length !== 0) {
    table = (
      <div className="table">
        <DataGrid
          rows={rows}
          columns={columns}
          pageSize={10}
          checkboxSelection
          onSelectionModelChange={(itm) => setRowSelection(itm)}
        />
        <CSVLink
          data={rows}
          filename={"pii.csv"}
          className="download-btn"
          target="_blank"
        >
          Export CSV
        </CSVLink>
      </div>
    );
  }

  return (
    <div className="App">
      <form onSubmit={getPIIHandler}>
        <FormControl style={{ width: "60%", margin: 5 }}>
          <InputLabel htmlFor="my-input">Enter URL</InputLabel>
          <Input
            type="url"
            id="url"
            value={inputURL}
            aria-describedby="my-helper-text"
            onChange={inputHandler}
          />
          <FormHelperText id="my-helper-text">
            kindly provide .git url only.
          </FormHelperText>
        </FormControl>
        <Button
          disabled={!inputURL}
          type="submit"
          variant="contained"
          color="primary"
        >
          Get Data
        </Button>
      </form>

      {loading ? <LinearProgress /> : ""}
      {table}
    </div>
  );
}

export default App;
