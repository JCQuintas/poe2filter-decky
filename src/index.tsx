import { ButtonItem, Navigation, PanelSection, PanelSectionRow, staticClasses } from "@decky/ui";
import { callable, definePlugin } from "@decky/api";
import { FaFilter } from "react-icons/fa";

const armAutoLogin = callable<[], void>("arm_auto_login");

function open() {
  armAutoLogin();
  Navigation.NavigateToExternalWeb("https://poe2filter.com/");
  Navigation.CloseSideMenus();
}

function Content() {
  return (
    <PanelSection>
      <PanelSectionRow>
        <ButtonItem
          layout="below"
          description="Tap Log in on the site. The Steam sign-in steps are clicked for you for the next 5 minutes."
          onClick={open}
        >
          Open poe2filter.com
        </ButtonItem>
      </PanelSectionRow>
    </PanelSection>
  );
}

export default definePlugin(() => ({
  name: "poe2filter",
  titleView: <div className={staticClasses.Title}>poe2filter</div>,
  content: <Content />,
  icon: <FaFilter />,
}));
