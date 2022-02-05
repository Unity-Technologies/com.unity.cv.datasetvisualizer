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
  startAt: number
}

class ItemSelector extends StreamlitComponentBase<State> {
  public state: State = {startAt: this.props.args["startAt"]}

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
    let increment = this.props.args["incrementAmt"]
    let index = this.state.startAt
    if(side === "left") {
      index -= increment
    } else if (side === "right") {
      index += increment
    }
    index = this.forceBounds(index)
    this.setState(
      () => ({startAt: index}),
      () => Streamlit.setComponentValue(this.state.startAt)
    )
  }

  private handleIndexChange = (value: string) => {
    let index = this.forceBounds(Number(value))

    this.setState(
      () => {
        return ({startAt: index})
      },
      () => Streamlit.setComponentValue(this.state.startAt)
    )
  }

  public render = (): ReactNode => {

    const Arrow = styled(ArrowForwardIosIcon)({
    })
    const FlippedArrow = styled(ArrowForwardIosIcon)({
      transform: "rotate(180deg)",
      color: this.props.disabled || this.state.startAt === 0 ? "#888" : this.props.theme?.primaryColor
    })
    const FixedMarginIconButton = styled(IconButton)({
      marginBottom: "10px",
      color: this.props.disabled || this.state.startAt + this.props.args["incrementAmt"] > this.props.args["datasetSize"]-1 ? "#888" : this.props.theme?.primaryColor
    })

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
            <p style={{fontFamily: "IBM Plex Sans, sans-serif", fontSize:"1rem", color: this.props.theme?.textColor}}>
              Go to frame #:
            </p>
            <TextField
              label="Index"
              id="outlined-size-small"
              defaultValue=""
              type="number"
              variant="outlined"
              size="small"
              disabled={this.props.disabled}
              onChange={e => this.handleIndexChange(e.target.value)}
              style={{
                marginBottom: "20px",
                marginTop: "-10px",
              }}
            />
          </div>
          <div style={{fontFamily: "IBM Plex Sans, sans-serif", width: "50%", display: "inline-block" }}>
            <div style={{ color:this.props.theme?.primaryColor, position: "relative", width: "300px", overflow: "visible", display: "block", marginLeft: "auto", marginRight: "auto" }}>
              <FixedMarginIconButton color="inherit"
                                     disabled={this.props.disabled || this.state.startAt === 0}
                                     onClick={() => this.handleClick("left")}
                                     style={{border: "1px solid #DDD", padding: "2px", borderRadius:"5px", marginRight: "10px"}}

              >
                <FlippedArrow fontSize="large"></FlippedArrow>
              </FixedMarginIconButton>
              <h1 style={{ color:"#666", fontWeight: "normal", display: "inline-block" }}>{this.state.startAt} - {Math.min(this.state.startAt + this.props.args["incrementAmt"]-1, this.props.args["datasetSize"] - 1)}</h1>
              <FixedMarginIconButton color="inherit"
                                     disabled={this.props.disabled || this.state.startAt + this.props.args["incrementAmt"] > this.props.args["datasetSize"]-1}
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

export default withStreamlitConnection(ItemSelector)

