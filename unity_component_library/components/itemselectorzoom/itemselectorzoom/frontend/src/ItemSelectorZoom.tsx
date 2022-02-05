import {
  Streamlit,
  withStreamlitConnection,
  StreamlitComponentBase
} from "streamlit-component-lib"
import React, { ReactNode} from "react"
import IconButton from '@material-ui/core/IconButton';
import ArrowForwardIosIcon from '@material-ui/icons/ArrowForwardIos';
import { styled, TextField } from "@material-ui/core"

interface State {
  index: number
}

class ItemSelectorZoom extends StreamlitComponentBase<State> {
  public state = {index: this.props.args["index"]}

  private forceBounds(index: number){
    let max_size = this.props.args["datasetSize"] - 1
    if (index < 0){
      index = 0
    } else if (index > max_size) {
      index = max_size
    }
    return index
  }

  private handleClick = (side: string): void => {
    let increment = 1
    let index = this.state.index
    if(side === "left") {
      index -= increment
    } else if (side === "right") {
      index += increment
    }
    index = this.forceBounds(index)
    this.setState(
      () => ({index: index}),
      () => Streamlit.setComponentValue(this.state.index)
    )
  }

  private handleIndexChange = (value: string) => {
    let index = this.forceBounds(Number(value))

    this.setState(
      () => {
        return ({index: index})
      },
      () => Streamlit.setComponentValue(this.state.index)
    )
  }

  public render = (): ReactNode => {

    const Arrow = styled(ArrowForwardIosIcon)({})
    const FlippedArrow = styled(ArrowForwardIosIcon)({
      transform: "rotate(180deg)",
      color: this.props.disabled || this.state.index === 0 ? "#888" : this.props.theme?.primaryColor
    })
    const FixedMarginIconButton = styled(IconButton)({
      marginBottom: "10px",
      color: this.props.disabled || this.state.index + 1 === this.props.args["datasetSize"] ? "#888" : this.props.theme?.primaryColor
    })
    const maxSize = this.props.args["datasetSize"]
    return (
        <div style={{width: "100%"}}>
          <style dangerouslySetInnerHTML={{__html: `
            .MuiOutlinedInput-notchedOutline {
              border-color: `+ this.props.theme?.primaryColor +` !important;
            }
            .MuiFormLabel-root {
              color: `+ this.props.theme?.textColor +` !important;
            }
            .MuiInputBase-input {
              color: `+ this.props.theme?.textColor +` !important;
            }
            .MuiOutlinedInput-notchedOutline:hover {
              border-color: `+ this.props.theme?.primaryColor +` !important;
            }
            .MuiFormLabel-root:hover {
              color: `+ this.props.theme?.textColor +` !important;
            }
            .MuiInputBase-input:hover {
              color: `+ this.props.theme?.textColor +` !important;
            }
            .MuiOutlinedInput-notchedOutline:focus {
              border-color: `+ this.props.theme?.primaryColor +` !important;
            }
            .MuiFormLabel-root:focus {
              color: `+ this.props.theme?.textColor +` !important;
            }
            .MuiInputBase-input:focus {
              color: `+ this.props.theme?.textColor +` !important;
            }
          `}} />
          <div style={{width: "50%", display: "inline-block"}}>
            <p style={{fontFamily: "\"IBM Plex Sans\", sans-serif", fontSize:"1rem", color: this.props.theme?.textColor}}>
              Go to frame #:
            </p>
            <TextField
              label="Index"
              id="outlined-size-small"
              defaultValue=""
              type="number"
              variant="outlined"
              size="small"
              color="secondary"
              disabled={this.props.disabled}
              onChange={e => this.handleIndexChange(e.target.value)}
              style={{
                marginBottom: "20px",
                marginTop: "-10px",
              }}
            />
          </div>
          <div style={{fontFamily: "IBM Plex Sans, sans-serif", width: "50%", display: "inline-block" }}>
            <div style={{color:"#F63366",  position: "relative", width: "300px", overflow: "visible", display: "block", marginLeft: "auto", marginRight: "auto" }}>
              <FixedMarginIconButton color="inherit"
                                     disabled={this.props.disabled || this.state.index === 0}
                                     onClick={() => this.handleClick("left")}
                                     style={{border: "1px solid #DDD", padding: "2px", borderRadius:"5px", marginRight: "10px"}}
              >
                <FlippedArrow fontSize="large" />
              </FixedMarginIconButton>
              <h1 style={{ color:"#666", fontWeight: "normal", display: "inline-block" }}>{this.state.index}</h1>
              <FixedMarginIconButton color="inherit"
                                     disabled={this.props.disabled || this.state.index + 1 === maxSize}
                                     onClick={() => this.handleClick("right")}
                                     style={{border: "1px solid #DDD", padding: "2px", borderRadius:"5px", marginLeft: "10px"}}
              >
                <Arrow fontSize="large" />
              </FixedMarginIconButton>
            </div>
          </div>
        </div>
    )
  }
}

export default withStreamlitConnection(ItemSelectorZoom)

