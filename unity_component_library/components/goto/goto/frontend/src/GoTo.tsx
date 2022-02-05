import {
  Streamlit,
  withStreamlitConnection,
  StreamlitComponentBase
} from "streamlit-component-lib"
import React, { ReactNode} from "react"
import { TextField } from "@material-ui/core"


interface State {
  index: number
}

class GoTo extends StreamlitComponentBase<State> {
  public state = {index: 0}

  private handleIndexChange = (value: string) => {
    this.setState(
      () => {
        return ({index: Number(value)})
      },
      () => Streamlit.setComponentValue(this.state.index)
    )
  }

  public render = (): ReactNode => {
      return (
          <div style={{
              display: "flex"
          }}>
              <p>Start at index:</p>
              <TextField
                  label="Index"
                  id="outlined-size-small"
                  defaultValue=""
                  type="number"
                  variant="outlined"
                  size="small"
                  onChange={e => this.handleIndexChange(e.target.value)}
                  style={{
                      marginBottom: "20px",
                      marginTop: "-10px",
                  }}
              />
          </div>
      );
  }
}

export default withStreamlitConnection(GoTo)

