import {
  Streamlit,
  withStreamlitConnection,
  StreamlitComponentBase
} from "streamlit-component-lib"
import React, { ReactNode} from "react"
import IconButton from '@material-ui/core/IconButton';
import ArrowForwardIosIcon from '@material-ui/icons/ArrowForwardIos';
import { styled } from "@material-ui/core"


interface State {
  index: number
}

class ImageSelector extends StreamlitComponentBase<State> {
  public state = {index: this.props.args["index"]}

  private handleClick = (side: string): void => {
    if(side === "left") {
      this.setState(
        prevState => ({index: prevState.index - 1}),
        () => Streamlit.setComponentValue(this.state.index)
      )
    } else if (side === "right") {
      this.setState(
        prevState => ({index: prevState.index + 1}),
        () => Streamlit.setComponentValue(this.state.index)
      )
    }
  }

  public render = (): ReactNode => {

    const Arrow = styled(ArrowForwardIosIcon)({})
    const FlippedArrow = styled(ArrowForwardIosIcon)({
      transform: "rotate(180deg)"
    })
    const FixedMarginIconButton = styled(IconButton)({
      marginBottom: "10px"
    })

    return (
      <div style={{ width: "100%" }}>
        <div style={{ position: "relative", width: "300px", overflow: "visible", display: "block", marginLeft: "auto", marginRight: "auto" }}>
          <FixedMarginIconButton color="primary"
                                 disabled={this.props.disabled}
                                 onClick={() => this.handleClick("left")}
          >
            <FlippedArrow fontSize="large" />
          </FixedMarginIconButton>
          <h1 style={{ display: "inline-block" }}>{this.state.index}</h1>
          <FixedMarginIconButton color="primary"
                                 disabled={this.props.disabled}
                                 onClick={() => this.handleClick("right")}
          >
            <Arrow fontSize="large" />
          </FixedMarginIconButton>
        </div>
      </div>
    )
  }
}

export default withStreamlitConnection(ImageSelector)

