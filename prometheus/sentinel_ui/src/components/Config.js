import React, { Component } from 'react';
import axios from 'axios';


class Config extends Component {
  state = {
    bcAgentConfig: {},
  };

  componentDidMount() {
    this.getConfig();
  }

  async getConfig() {
    axios.get("/api/config").then((response)=>{
        this.setState(()=>{
           return {
             bcAgentConfig: response.data
           }
        })
    });
  }

  render() {
    return (
        <pre>{JSON.stringify(this.state.bcAgentConfig, null, 2)}</pre>
    );
  }
}

export default Config;