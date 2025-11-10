![][image1]*July 2025* 

**Multi-Actor Generative Artificial Intelligence as a Game Engine** 

**Alexander Sasha Vezhnevets**1**, Jayd Matyas**1**, Logan Cross**1**, Davide Paglieri**1**, Minsuk Chang**1**, William A. Cunningham**1, 2**, Simon Osindero**1**, William S. Isaac**1 **and Joel Z. Leibo**1 

1Google DeepMind, 2University of Toronto 

**Generative AI can be used in multi-actor environments with purposes ranging from social science modeling to interactive narrative and AI evaluation. Supporting this diversity of use cases—which we classify as Simulationist, Dramatist, and Evaluationist—demands a flexible scenario definition framework.** arXiv:2507.08892v1 \[cs.AI\] 10 Jul 2025  
**We argue here that a good approach is to take inspiration from tabletop role-playing games (TTRPGs), where a Game Master (GM) is responsible for the environment and generates all parts of the story not directly determined by the voluntary actions of player characters. We argue that the Entity-Component architectural pattern is useful here. In such a system, the GM is not a hardcoded computer game but is itself a configurable entity, composed of components just like any other actor. By design, the approach allows for a separation between the underlying implementation details handled by an engineer, the creation of reusable components, and their composition and configuration managed by a designer who constructs entities from the components. This separation of concerns is instrumental for achieving rapid iteration, maintaining modularity, and ultimately to ensure scalability. We describe the ongoing evolution of the Concordia library in terms of this philosophy, demonstrating how it allows users to effectively configure scenarios that align with their specific goals.** 

**Contents** 

**1 Introduction 1 2 Entities, Components, Engines, and Game Design 3** 

**3 Mapping the space of potential game/simulation design objectives 5** 3.1 The Evaluationist Perspective . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 6 3.2 The Dramatist Perspective . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 6 3.3 The Simulationist Perspective . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 7 

**4 Discussion 8** 4.1 Synthetic Data Generation: A Cross-Cutting Concern . . . . . . . . . . . . . . . . . . 8 4.2 Design Trade-offs and System Purpose . . . . . . . . . . . . . . . . . . . . . . . . . . 9 4.3 Implications for Multi-Actor System Definition Language Design . . . . . . . . . . . . 9 

**5 Conclusion 10** 

**1\. Introduction** 

The space of fruitful application for “agentic” generative artificial intelligence (AI) is rapidly expanding beyond single-actor systems into complex multi-actor environments (Guo et al., 2024; Han et al., 2024; Li et al., 2023; Park et al., 2023; Sunehag and Leibo, 2025; Vezhnevets et al., 2023; Yang et al., 2025). These systems are being developed for a wide range of purposes: generating compelling   
Multi-Actor Generative Artificial Intelligence as a Game Engine 

narratives (Mirowski et al., 2023; Wu et al., 2024), modeling tools for social and psychological science (Anthis et al., 2025; Grossmann et al., 2023; Hewitt et al., 2024; Horton, 2023; Kozlowski et al., 2024; Park et al., 2024), sandboxes for problem solving teamwork (Gong et al., 2023; Shao et al., 2024; Zeng et al., 2024; Zhang et al., 2023), evaluation frameworks (Guertler et al., 2025; Zhou et al., 2023) and synthetic data sources (Duéñez-Guzmán et al., 2023; Liu et al., 2025; Motwani et al., 2024; Silver and Sutton, 2025). This diversity in application domains suggests it will be useful to carefully consider underlying architecture and design philosophies to make sure flexibility over all the relevant use cases can be maintained without adding too much complexity. 

To better frame the diverse applications of these systems, we propose a typology of user motivations taking inspiration from game design theory (specifically Edwards (2004)). We delineate three distinct motivations for defining generative multi-actor scenarios: (A) Evaluationist, (B) Dramatist, and (C) Simulationist. The Evaluationist seeks to create controlled environments to benchmark and compare AI capabilities, their most important requirement is for the system to be a fair and rigorous testbed (Section 3.1). The Dramatist aims to generate compelling, coherent narratives and rich character interactions, using the system as an interactive storytelling engine (Section 3.2). Finally, the Simulationist uses the system as a “pocket universe” to model and understand real-world social or causal dynamics with as much fidelity as possible (Section 3.3). We also discuss synthetic data generation for training further AI systems as a cross-cutting concept with connection to all three motivations (Section 4.1). Such datasets can be used as curricula to train new AI systems. In this view, a Dramatist configuration becomes a ‘story factory’, capable of generating endless narrative examples to forge more creative and empathetic models. Data from Simulationist scenarios can be used to imbue an AI with greater understanding of complex social and physical dynamics. Likewise, an Evaluationist framework can serve as a diagnostic engine, producing fine-grained behavioral data across controlled conditions to enable precise, quantitative comparisons between different models. Which motivation becomes most salient depends on the ultimate goal of the work (Evaluationist, Dramatist, or Simulationist). We will argue that the requirements of effectively serving any of these distinct goals can be achieved in single library of sufficient flexibility. 

The original Concordia (Vezhnevets et al., 2023) was conceived as a generative agent-based modeling library (GABM) composed of two generative parts: a model of individual actors and a model of the environment, which was termed the Game Master (GM)—both based on large language models. The GM, inspired by the storyteller role in tabletop role-playing games (Gygax and Cook, 1989), was responsible for generating the setting and context for social interactions of the individual actors. The “players” in the TTRPG context are identified with the individual decision makers of agent-based modeling. 

The subsequent development of Concordia maintains the inspiration from table-top role-playing games while evolving toward a technical design philosophy aligned with modern game engines like Unity 3D (Unity Technologies). The core of this evolution is the principled adoption of the Entity Component architectural pattern. An Entity is a simple, unique identifier—essentially a container. A Component is a reusable module of data that defines a specific aspect of an entity, such as its memory, physical state, or goals. An entity’s properties and behaviors emerge from the specific collection of components attached to it. While entities often represent individual agents, the flexibility of this pattern means an entity can also represent a collective, such as a company, a government agency, a social group, or a legal body like a court. Their Components would then pertain to the collective attributes and functions of that organization, like accounting ledgers and court proceedings. 

In terms of Concordia’s TTRPG interpretation, both the players and the game master are entities. An entity’s functionality is defined by its components. 

The Entity-Component architectural choice is the technical foundation for our design philosophy, 2  
Multi-Actor Generative Artificial Intelligence as a Game Engine 

which separates the concerns of the ‘engineer’ and the ‘designer’. The engineer uses the Concordia framework to build stable, reusable, and testable components (e.g., a new planning algorithm or a specific memory model1). The designer uses existing entities and components as building blocks to craft scenarios, often without writing new component-level code. 

We argue that this separation is very helpful in a multi-actor generative AI platform. It allows a user to focus entirely on their design goal—be it Evaluationist, Dramatist, or Simulationist—by configuring existing components, while another developer can extend the platform’s fundamental capabilities. Even if there is only a single person playing both roles, the separation of concerns between design and engineering is still helpful, both for enabling rapid experimentation at the design level and stable, systematic development at the engineering level. 

**2\. Entities, Components, Engines, and Game Design** 

The Entity-Component architectural pattern, a cornerstone of modern game development Gregory (2018); Nystrom (2014); Raffaillac and Huot (2019), provides a powerful and flexible foundation for building multi-actor generative AI systems that can be effectively tailored to different design goals. An Entity-Component framework utilizes composition instead of inheritance, as entities are not defined by a rigid class structure. Instead, they are independent lightweight objects with unique identifiers. Their behaviors and properties are determined by the components attached to them (i.e. an entity is a box of components with a name). The engine (i.e. a “system” in strict entity-component-system terminology) is responsible for processing entities by calling functions such as ‘observe’ and ‘act’ on all entities with components implementing those functions. 

Components are created by combining Python code with LLM calls. This allows for maximal flexibility and expressivity. When the designer knows how to code a specific feature they are welcome to do so; simultaneously, other features in the same environment can be implemented by asking the GM storyteller LLM to implement them. Both kinds of functionality generally exist in the same environment. You can give the GM freedom to create whatever its LLM comes up with, or you can constrain it to stay very close to established, and hard-coded, guardrails—and everything in between. 

There are two main calls on an entity: observe and act. 

When observe is called, this triggers preobserve and postobserve functions to be called on every component to process observations for each entity. When act is called, each component plays one of two distinct roles: 

• **Context**—These can be numerous and diverse. They initially process the action request in parallel, each contributing information or updating its internal state. Their outputs are ag gregated to form a comprehensive contextual understanding for the entity. After an action is determined, these components are again engaged to react to the outcome. For example, a SelfReflection context component asks “What kind of person am I?” and feeds the LLM’s response to subsequent components (as described in Vezhnevets et al. (2023) and Leibo et al. (2024)). 

• **Acting**—Each entity has exactly one component designated as the Acting component. This restriction to a single acting component reflects a basic assumption that an actor takes exactly one action per step. Note that the amount of time passing between steps is entirely arbitrary so this is not a restrictive assumption. Knowing there will be at most one action per entity per step makes it natural to view the Acting component as an aggregator of information received 

1Components often use RAG internally, see Vezhnevets et al. (2023). This is similar to Park et al. (2023). 3  
Multi-Actor Generative Artificial Intelligence as a Game Engine 

from a set of Context components. It receives information from calling preact on all Context Components, and an action request from the engine (i.e. ultimately from another entity, such as the GM). The Acting component’s unique responsibility is to synthesize all this input to decide and return the entity’s final, singular action (for the current timestep). This clear division of labor—many components providing and reacting to context, and one component deciding the action—underpins the system’s flexibility. It allows testing of variable decision-making strategies by interchanging the Acting component while retaining the same suite of Context Components. After the Acting component returns the action, postact is called on all components. 

In practice, when implementing a Concordia component, what you actually do is you implement preobserve, postobserve, preact, and postact (or any subset of these). It is very common to implement either the observation methods or the action methods and rare to implement both kinds on the same component. 

The modularity of components allows for the easy creation of diverse entities with different functionality by mixing and matching components. This contrasts with traditional object-oriented approaches where creating new types of actors with slightly different behaviors can lead to complex and brittle inheritance chains. For generative AI agents, this is particularly beneficial. An agent’s “mind” can be composed of various components: a Memory component for storing past experiences, a Planning component that uses a large language model to generate goals, and a Beliefs component to represent its understanding of the world. Similarly, an organizational entity could be composed of components representing its departments, policies, and internal communication structures. Different agents can be endowed with different cognitive architectures by simply equipping them with different sets of components. This modularity makes the framework very scalable. It can support scenarios ranging from a simple dialogue between two actors in a chat room to a complex economic simulation with thousands of agents and external events like natural disasters. 

The flexibility of this architectural pattern also extends to the Game Master (GM) within the Concordia framework. The GM is also an entity and can be customized with components, just like player entities (actors). This allows the GM’s role and logic to be tailored to the specific needs of the multi-actor system, whether that be enforcing strict evaluation protocols, guiding narrative development, or maintaining causal consistency. The use of prefabs, or pre-configured collections of components (which can be cloned and subsequently modified), can further streamline the process of creating and customizing both actors and GMs. 

The Concordia framework also accommodates diverse interaction dynamics through several game engines. A simultaneous engine allows all actors to act in parallel within the same time step, useful for modeling scenarios like market trading where all actors submit their buy/sell orders at the same time. In contrast, a sequential engine enforces turn-based interactions—such as dialogue—with an order that is either predetermined or dynamically generated by the Game Master. The framework also supports fully asynchronous operation, which is ideal for modeling environments like social media where users can act at any time, independent of others. This flexibility can also be used to speed up or scale up simulations via concurrency. 

One goal in designing these language features, both here and in the game engines like Unity Technologies that inspired us, was to allow for a differentiation in role between game designers and game engineers. Of course, actual differentiation of roles is optional (and unlikely in small teams). Nevertheless, the modularity enforced by designing around the designer/engineer dichotomy is helpful for everyone in terms of facility for defining robust and flexible scenarios. The distinction between engineer and designer in Concordia reflects a deliberate prioritization: the system is built to make design work possible without constant engineering support. Users should be able to set up 

4  
Multi-Actor Generative Artificial Intelligence as a Game Engine 

complex meaningful scenarios without needing to write new component-level code. This mirrors workflows in modern game engines like Unity, which are structured to let designers build and test systems by combining multiple parts (Fullerton, 2008) In the context of generative multi-actor systems, this makes Concordia especially well-suited for rapid hypothesis testing, scenario exploration, and iterative modeling of social dynamics. 

**3\. Mapping the space of potential game/simulation design objectives** 

Taking inspiration from “System Does Matter2” (Edwards, 2004), we discuss the varieties of applica tions and kinds of multi-actor3 generative AI approaches. Just as there are three kinds of tabletop role-playing gamers (or three motivations for playing tabletop role-playing games (TTRPG), there are analogous categories for the users of multi-actor generative AI system design libraries. According to Edwards (2004), the categories for TTRPGs are: (1) Gamist, (2) Narrativist, and (3) Simulationist. The Gamist wants the system to be fair and balanced, and to afford the possibility of victory while maintaining danger of defeat. The Narrativist wants the result to be a good story. The Simulationist wants a “little pocket universe without fudging” Edwards (2004)—they seek realistic projection from initial conditions. 

We will argue here that users of multi-actor generative AI also have a range of different motivations and that a specific classification schema is helpful for understanding their diversity. It is important, however, to clarify how we are adapting this analogy. Whereas Edwards used his model to categorize system types and their internal mechanics, we use this framework to describe the different goals a user might bring when configuring an environment. The framework characterizes user intent, not a prescription for how a system ought to be designed. This distinction is key to our argument that a flexible platform can be configured to serve any of these user goals. 

With that in mind, we find it helpful to consider the motivations for using multi-actor generative AI as belonging to one of the following types: (1) Evaluationist (analogous to Edwards (2004)’s Gamist), (2) Dramatist (analogous to Edwards (2004)’s Narrativist), and (3) Simulationist (analogous to Edwards (2004)’s category of the same name). The Evaluationist wants to evaluate the performance of AI systems, determine which are better or worse and in which applications and contexts, the Dramatist wants the multi-actor system to function well as a story generator, and the Simulationist wants the multi-actor system to function as a modeling tool for forecasting and social science research. Our Edwards (2004)-inspired framework is also related to another influential game design framework called MDA (Hunicke et al., 2004), which separates game systems into Mechanics (implementation level rules), Dynamics (emergent behavior during execution), and Aesthetics (intended outcomes or system-level goals). 

Generative AI also has a fourth motivation which may perhaps be its own primary category, or may instead be considered a background objective that permeates all three primary objectives and colors them: this is the objective of creating synthetic training data (see Section 4.1). We think it is better to view synthetic data generation as a background goal because the generated data will itself always have to be data suitable for a specific purpose. If the purpose is to improve the AI system’s fiction writing and understanding then the data-generating multi-actor system will be constructed in accord with the Dramatist motivation. If the purpose is to improve the AI system’s realistic understanding of social or physical causality then the motivation for the data generating multi-actor system is Simulationist. 

2http://www.indie-rpgs.com/\_articles/system\_does\_matter.html   
3Note that we have started using the term ‘actor” as opposed to the term “agent” since we think it is likely that the term “agent” will soon be synonymous with a category of tech product and rapidly lose its original meaning, the same semantic transformation that recently occurred for the word “hallucination”. 

5  
Multi-Actor Generative Artificial Intelligence as a Game Engine 

**3.1. The Evaluationist Perspective** 

The Evaluationist approach to multi-actor generative AI systems parallels Edwards (2004)’s Gamist motivation in TTRPGs. Where the Gamist seeks fair contests with opportunities for strategic victory, the Evaluationist approaches multi-actor systems as frameworks for assessment and comparison. We have taken this perspective in benchmark-oriented research such as the Concordia Contest (Smith et al., 2025), which evaluated the generalization capabilities of LLM-based actors in mixed-motive scenarios. 

For Evaluationist users, the primary objective is clear: to determine which AI systems perform better across specified dimensions and contexts. This requires environments that provide a “fair playing field” with well-defined metrics for success. Systems designed with this motivation prioritize balanced starting conditions, consistent evaluation protocols, and reproducible outcomes. The focus is not on narrative coherence or simulation fidelity per se, but rather on creating conditions that allow for meaningful comparison between different agent implementations. 

Evaluationist systems typically feature: 

• **Standardized scenarios**—Carefully calibrated environments that present consistent challenges across multiple evaluation runs 

• **Clear success metrics**—Quantifiable measures of performance that allow for unambiguous ranking of different approaches 

• **Controlled variability**—Strategic introduction of novel elements to assess generalization capa bilities 

• **Cross-play mechanics**—Methods for evaluating how agents perform when interacting with different partner populations 

In the Concordia NeurIPS competition (Smith et al., 2025), the evaluation emphasized zero-shot generalization—the ability of agents to transfer strategies to novel social contexts. This methodological approach mirrors principles from supervised learning research, where performance on previously unseen data is considered the gold standard for evaluation. The contest structure, with its distinct development and evaluation phases, is an example of the way in which adopting the Evaluationist motivation has implications for system design. 

Furthermore, the Evaluationist can use this framework not just to test overall model capability, but to diagnose why an agent succeeds or fails. Because agents are composed of modular components that form a structured chain of thought, a researcher can build, test, and refine specific cognitive architectures (‘decision logics’ in the terminology of Leibo et al. (2024)). For example, if an agent consistently fails at a negotiation task, the Evaluationist can swap out its Planning component or add a new SocialReasoning component to investigate and fix the specific point of failure in its decision-making. 

**3.2. The Dramatist Perspective** 

In contrast to the Evaluationist, the Dramatist views multi-actor generative AI systems primarily as narrative engines. This motivation aligns with Edwards (2004)’s Narrativist player, who is “satisfied if a roleplaying session results in a good story.” For a user with a Dramatist goal, the central concern is not benchmarking performance but generating compelling narratives through the interactions of multiple AI actors. Multi-actor systems for narrative-driven computer games are often of this type. 

From the designer’s perspective, a system built for a Dramatist purpose will prioritize narrative coherence, emotional resonance, and dynamic character development over standardized evaluation. 

6  
Multi-Actor Generative Artificial Intelligence as a Game Engine 

This leads to a focus on features such as: 

• **Rich character models** – Detailed personas with well-defined goals, values, and relationships, often constructed by composing multiple components 

• **Narrative-driven environments** – Settings designed to elicit dramatically interesting interac tions 

• **Flexible resolution mechanisms** – Systems that prioritize narrative satisfaction over procedural consistency 

• **Emergent story arcs** – Frameworks that allow for the development of compelling narrative trajectories without predetermined outcomes 

Achieving these narrative goals is a quintessential task for the game designer. Within the Con cordia framework, the designer can leverage the modularity of the Entity-Component architecture to orchestrate the story. For example, the Game Master (GM) entity can be configured with specific components to function as a "narrative director." A designer might give the GM components that create distinct protagonist and antagonist roles among the actors, and then manage information asymmetry between them. An antagonist character, for example, could be given knowledge of future plot points, such as events in a third act, while the protagonist remains unaware, thereby heightening dramatic tension. Alternatively, the GM can be configured to facilitate a dynamic, player-driven experience, essentially creating an open-ended “choose-your-own-adventure” storyline. Jenkins (2004) frames this as a distinction between *embedded* and *emergent* narrative structure—the GM can either lay out key events in advance or let narrative arcs take shape through interaction. Concordia supports both approaches, depending on how the scenario is configured. This model is similar to that of games like AI Dungeon4, where the player’s freeform text choices direct an LLM to generate worlds, characters, and scenarios in real-time. This approach is part of a broader effort to use generative AI for creating dynamic storylines that adapt to player choices, moving beyond traditional branching narratives toward truly emergent storytelling (Gallotta et al., 2024; Korsah, 2025). 

**3.3. The Simulationist Perspective** 

The Simulationist approach parallels its TTRPG counterpart, seeking to create “a little pocket universe without fudging” (Edwards, 2004). For these users, the goal is to model real-world processes with enough fidelity to generate insights into complex social, economic, or physical phenomena (Anthis et al., 2025). This perspective directly addresses a long-standing challenge in the social sciences. For decades, Agent-Based Models (ABMs) have been a vital tool, but their power has been limited by the need for simplifying assumptions about agents and their environments (Poteete et al., 2010). Often, agents are modeled as simple, rational reward-maximizers, and environments are reduced to a few variables, which limits the kinds of phenomena that can be studied (Schill et al., 2019). 

The goal of a Simulationist using Concordia is to try to realize the original promise of ABMs. This is achieved in two primary ways. First, by populating simulations with more psychologically and sociologically plausible actors. Unlike agents in traditional ABMs or even many multi-agent reinforcement learning systems (see Hertz et al. (2025)), Concordia models can be defined without any need for a scalar reward signal. Entities in the simulations act via “pattern completion” based on their identity and experience (Leibo et al., 2024). This allows for the modeling of nuanced social dynamics—such as the spread of identity-based gossip or how arbitrary social norms are negotiated— that were previously too difficult to capture computationally. Second, Concordia allows for greater environmental fidelity, as the GM can generatively manage open-ended world details, freeing the designer to code only the specific environmental mechanics critical to their research question. 

4https://aidungeon.com/ 

7  
Multi-Actor Generative Artificial Intelligence as a Game Engine 

A designer with a Simulationist motivation is not adhering to a rigid structure, but instead focuses on a set of priorities tailored to their research question. Here is a menu of goals that a Simulationist may choose to emphasize: 

• **Predictive validity**—Designing systems capable of generating predictions that can be validated against real-world outcomes 

• **Causal consistency**—Ensuring that system mechanics reflect theoretically sound causal rela tionships 

• **Empirical grounding**—Basing agent behaviors and environmental responses on empirical observations where possible 

• **Emergent complexity**—Allowing complex phenomena to emerge from the interaction of simple rules and components rather than being explicitly programmed 

Within the Simulationist perspective, it’s useful to distinguish between the goals of prediction and simulation itself. Prediction focuses primarily on the accuracy of forecasting future outcomes, regardless of whether the prediction gathers any insight into the underlying process. In contrast, simulation prioritizes the fidelity of the model’s of real-world mechanisms. A successful simulation should ideally yield accurate predictions (demonstrating predictive validity), but the core Simulationist drive often lies in using the model as a laboratory: to explore counterfactuals, understand systematic behavior, and gain insight into the causal levers. 

The Entity-Component architecture is key to achieving these goals. The engineer provides a library of components with varying trade-offs in fidelity and computational cost. The designer then composes a model at the appropriate level of abstraction for their question—from using a simple RationalActor component for a large-scale economic forecast to a more complex BeliefsAndReasoning component for a small-group study. This allows for the iterative refinement needed to ensure the system’s behavior aligns with real-world data, prioritizing causal consistency and explanatory power. 

**4\. Discussion** 

**4.1. Synthetic Data Generation: A Cross-Cutting Concern** 

Synthetic data generation represents a distinct motivation for users of multi-actor generative AI systems. However, rather than constituting a fourth primary category alongside Evaluationist, Dramatist, and Simulationist motivations, we argue that data generation functions more effectively as a cross-cutting concern that permeates and influences each primary category. 

Synthetic data generation is inherently purpose-driven. It serves goals such as enabling models to bootstrap their reasoning capabilities in verifiable domains (Guo et al., 2025; Yu et al., 2023; Zelikman et al., 2022), or curating vast amounts of high-quality, targeted data to train specialized models (Abdin et al., 2024a,b; Eldan and Li, 2023). This instrumental quality means that the design of data-generating systems will inevitably be colored by one of the three primary motivations: 

• **Evaluationist-driven data generation** focuses on creating balanced, representative datasets suitable for benchmarking and comparative assessment of AI systems, for example by procedu rally generating evaluations from templates (Gandhi et al., 2023). 

• **Dramatist-driven data generation** prioritizes creating rich, narratively complex interaction datasets that capture the nuances of character development and plot progression. This motivation also encompasses synthetic data designed to increase the creativity of the model’s outputs (Ismayilzada et al., 2025; Xu et al., 2025). 

8  
Multi-Actor Generative Artificial Intelligence as a Game Engine 

• **Simulationist-driven data generation** emphasizes producing data that accurately reflects real-world causal relationships and can be used to train models with strong predictive validity. 

**4.2. Design Trade-offs and System Purpose** 

Edwards (2004) argues that “a good system is one which knows its outlook and doesn’t waste any mechanics on the other two outlooks”. This principle is critical. A specific scenario cannot simultaneously serve Evaluationist, Dramatist, and Simulationist goals equally well; optimizing for one motivation inevitably involves trade-offs with the others. For instance, the flexible resolution mechanisms that serve a Dramatist by prioritizing narrative satisfaction may undermine the physical consistency prized by a Simulationist. 

However, this does not mean the underlying platform must be limited to just one of the motivating outlooks. Concordia is best understood by analogy to a general-purpose engine, not a specific game. A game engine like Unity can be used to create a first-person shooter, a role-playing game, or a puzzle game. While the engine is flexible enough for any of these, any single product that tried to be all three at once would likely fail. Similarly, Concordia provides a library of tools to build a focused experience. It supports all three motivations, but for any given scenario, the designer must choose a primary goal if they are to be effective. 

These trade-offs are shaped by the specific outcomes each configuration is designed to support. An Evaluationist system emphasises comparability and control, a Dramatist one centers narrative coherence and emotional significance, a Simulationist configuration prioritises causal fidelity and emergent dynamics. Each configuration reflects a choice about what kind of insight or output is most valuable. Salen and Zimmerman (2003) describe game “systems” as structures that shape meaning through their design choices. In Concordia, this idea is actualized for each particular scenario in the way specific configurations of sets of components influence not just what an actor will do but also what kinds of questions the scenario is set up to explore. In this way, scenario design becomes more than mechanics—it becomes a way of enacting a particular approach to answering (for a given context) how knowledge is acquired, validated, and what constitutes valuable understanding. See also Kommers et al. (2025) on cultural “thick description” with LLMs. 

The design choices made for an Evaluationist system reflect a commitment to obtaining knowledge through controlled comparison and quantifiable performance metrics. A Dramatist design prioritizes insights gained through the exploration of narrative possibilities and the emotional impact of the generated story. A Simulationist configuration, conversely, embodies a stance that seeks understanding through modeling complex interactions and observing emergent phenomena. Therefore, the chosen configuration shapes not just the system’s output, but also the way in which researchers and users engage with the system to learn and gain knowledge, highlighting the deliberate choice about what kind of truth or insight the system is intended to reveal. Concordia’s contribution is not to resolve these tensions but to make them configurable, allowing researchers to articulate and operationalize their modeling priorities through system design. 

**4.3. Implications for Multi-Actor System Definition Language Design** 

Concordia’s design philosophy is to empower the user in their role as a “game designer”. It includes templates—pre-configured prefabs—that work as appropriate starting points for users who have each of the three motivations, much like a game engine might offer a “First-Person Shooter” or “Role-Playing Game” template. 

This separation of roles is directly inspired by common practice in teams using engines like Unity 9  
Multi-Actor Generative Artificial Intelligence as a Game Engine 

(Unity Technologies). The designer workflow in Concordia mirrors that of a level designer in Unity, who can create new game entities by adding components and tweaking their parameters, often without writing new low-level code. For instance, a designer can ask: “What if this actor had a more limited memory but a stronger sense of social obligation?” They can answer this question by composing an actor with a specific Memory component and a SocialNorms component, then simply tuning the parameters on each. 

Meanwhile, the engineer workflow is what makes this powerful designer experience possible. An engineer would have first implemented that SocialNorms component as a self-contained, reusable Python class within the Concordia framework, deliberately exposing key parameters for the designer to adjust. This decoupling ensures that designers can rapidly prototype and experiment with complex behaviors on a stable foundation, while engineers can focus on building and validating robust, foundational tools without getting entangled in the specifics of any single scenario. 

**5\. Conclusion** 

The diverse applications of multi-actor generative AI—from scientific modeling to narrative generation and AI evaluation—demand a flexible and robust architectural foundation. The Entity-Component pattern, borrowed from game development, provides this foundation by separating the concerns of low-level engineering from high-level design. This allows a designer to rapidly prototype and configure complex scenarios by composing actors and environments from a library of reusable components. As demonstrated by the Concordia library, this approach empowers users to tailor systems to their specific Evaluationist, Dramatist, or Simulationist goals, advancing the capability and accessibility of generative multi-actor modeling. 

The present iteration, v2, provides the technical means to realize the vision of generative agent based modeling we have previously described (Leibo et al., 2024; Vezhnevets et al., 2023). By enabling actors who operate on complex verbal internal states through pattern-completion rather than simple reward maximization, this framework moves beyond the constraints of classical game theory and traditional agent-based models. It opens a new frontier where the lines between social science, interactive storytelling, and AI science begin to blur. By providing a common architectural foundation, Concordia offers a versatile space where Simulationists can build testable worlds, Dramatists can direct emergent narratives, and Evaluationists can forge rigorous benchmarks within the same unified framework. 

Concordia is available on github at https://github.com/google-deepmind/concordia. 

**References** 

M. Abdin, J. Aneja, H. Awadalla, A. Awadallah, A. A. Awan, N. Bach, A. Bahree, A. Bakhtiari, J. Bao, H. Behl, et al. Phi-3 technical report: A highly capable language model locally on your phone. *arXiv preprint arXiv:2404.14219*, 2024a. 

M. Abdin, J. Aneja, H. Behl, S. Bubeck, R. Eldan, S. Gunasekar, M. Harrison, R. J. Hewett, M. Javaheripi, P. Kauffmann, et al. Phi-4 technical report. *arXiv preprint arXiv:2412.08905*, 2024b. 

J. R. Anthis, R. Liu, S. M. Richardson, A. C. Kozlowski, B. Koch, J. Evans, E. Brynjolfsson, and M. Bern stein. LLM social simulations are a promising research method. *arXiv preprint arXiv:2504.02234*, 2025\. 

E. A. Duéñez-Guzmán, S. Sadedin, J. X. Wang, K. R. McKee, and J. Z. Leibo. A social path to human-like artificial intelligence. *Nature machine intelligence*, 5(11):1181–1188, 2023\. 

10  
Multi-Actor Generative Artificial Intelligence as a Game Engine 

R. Edwards. System does matter. *The forge*, 28, 2004\. 

R. Eldan and Y. Li. Tinystories: How small can language models be and still speak coherent english? *arXiv preprint arXiv:2305.07759*, 2023\. 

T. Fullerton. *Game Design Workshop: A Playcentric Approach to Creating Innovative Games*. Elsevier, 2008\. 

R. Gallotta, G. Todd, M. Zammit, S. Earle, A. Liapis, J. Togelius, and G. N. Yannakakis. Large language models and games: A survey and roadmap. *IEEE Transactions on Games*, 2024\. 

K. Gandhi, J.-P. Fränken, T. Gerstenberg, and N. Goodman. Understanding social reasoning in language models with language models. *Advances in Neural Information Processing Systems*, 36: 13518–13529, 2023\. 

R. Gong, Q. Huang, X. Ma, H. Vo, Z. Durante, Y. Noda, Z. Zheng, S.-C. Zhu, D. Terzopoulos, L. Fei-Fei, et al. Mindagent: Emergent gaming interaction. *arXiv preprint arXiv:2309.09971*, 2023\. 

J. Gregory. *Game engine architecture*. AK Peters/CRC Press, 2018\. 

I. Grossmann, M. Feinberg, D. C. Parker, N. A. Christakis, P. E. Tetlock, and W. A. Cunningham. Ai and the transformation of social science research. *Science*, 380(6650):1108–1109, 2023\. 

L. Guertler, B. Cheng, S. Yu, B. Liu, L. Choshen, and C. Tan. Textarena. *arXiv preprint arXiv:2504.11442*, 2025\. 

D. Guo, D. Yang, H. Zhang, J. Song, R. Zhang, R. Xu, Q. Zhu, S. Ma, P. Wang, X. Bi, et al. Deepseek-r1: Incentivizing reasoning capability in llms via reinforcement learning. *arXiv preprint arXiv:2501.12948*, 2025\. 

T. Guo, X. Chen, Y. Wang, R. Chang, S. Pei, N. V. Chawla, O. Wiest, and X. Zhang. Large language model based multi-agents: A survey of progress and challenges. *arXiv preprint arXiv:2402.01680*, 2024\. 

G. Gygax and D. Cook. *The Dungeon Master Guide, No. 2100, 2nd Edition (Advanced Dungeons and Dragons)*. TSR, Inc, 1989\. ISBN 0880387297\. 

S. Han, Q. Zhang, Y. Yao, W. Jin, and Z. Xu. LLM multi-agent systems: Challenges and open problems. *arXiv preprint arXiv:2402.03578*, 2024\. 

U. Hertz, R. Köster, M. A. Janssen, and J. Z. Leibo. Beyond the matrix: Experimental approaches to studying cognitive agents in social-ecological systems. *Cognition*, 254:105993, 2025\. 

L. Hewitt, A. Ashokkumar, I. Ghezae, and R. Willer. Predicting results of social science experiments using large language models. *Preprint*, 2024\. 

J. J. Horton. Large language models as simulated economic agents: What can we learn from homo silicus? Technical report, National Bureau of Economic Research, 2023\. 

R. Hunicke, M. LeBlanc, and R. Zubek. Mda: A formal approach to game design and game research. In *Proceedings of the AAAI Workshop on Challenges in Game AI*, 2004\. 

M. Ismayilzada, A. Laverghetta Jr, S. A. Luchini, R. Patel, A. Bosselut, L. van der Plas, and R. Beaty. Creative preference optimization. *arXiv preprint arXiv:2505.14442*, 2025\. 

11  
Multi-Actor Generative Artificial Intelligence as a Game Engine 

H. Jenkins. Game design as narrative architecture. In *First person: New media as story, performance, and game*, pages 118–130. MIT Press, 2004\. 

C. Kommers, D. Hemment, M. Antoniak, J. Z. Leibo, H. Long, E. Robinson, and A. Sobey. Meaning is not a metric: Using llms to make cultural context legible at scale. *arXiv preprint arXiv:2505.23785*, 2025\. 

A. Korsah. The impact of generative artificial intelligence in game development: a scoping review. 2025\. 

A. C. Kozlowski, H. Kwon, and J. A. Evans. In silico sociology: forecasting covid-19 polarization with large language models. *arXiv preprint arXiv:2407.11190*, 2024\. 

J. Z. Leibo, A. S. Vezhnevets, M. Diaz, J. P. Agapiou, W. A. Cunningham, P. Sunehag, J. Haas, R. Koster, E. A. Duéñez-Guzmán, W. S. Isaac, G. Piliouras, S. M. Bileschi, I. Rahwan, and S. Osindero. A theory of appropriateness with applications to generative artificial intelligence. *arXiv preprint arXiv:2412.19010*, 2024\. 

G. Li, H. Hammoud, H. Itani, D. Khizbullin, and B. Ghanem. CAMEL: Communicative agents for" mind" exploration of large language model society. *Advances in Neural Information Processing Systems*, 36:51991–52008, 2023\. 

B. Liu, L. Guertler, S. Yu, Z. Liu, P. Qi, D. Balcells, M. Liu, C. Tan, W. Shi, M. Lin, et al. Spiral: Self-play on zero-sum games incentivizes reasoning via multi-agent multi-turn reinforcement learning. *arXiv preprint arXiv:2506.24119*, 2025\. 

P. Mirowski, K. W. Mathewson, J. Pittman, and R. Evans. Co-writing screenplays and theatre scripts with language models: Evaluation by industry professionals. In *Proceedings of the 2023 CHI conference on human factors in computing systems*, pages 1–34, 2023\. 

S. R. Motwani, C. Smith, R. J. Das, R. Rafailov, I. Laptev, P. H. Torr, F. Pizzati, R. Clark, and C. S. de Witt. Malt: Improving reasoning with multi-agent llm training. *arXiv preprint arXiv:2412.01928*, 2024\. 

R. Nystrom. *Game programming patterns*. Genever Benning, 2014\. 

J. S. Park, J. O’Brien, C. J. Cai, M. R. Morris, P. Liang, and M. S. Bernstein. Generative agents: Interactive simulacra of human behavior. In *Proceedings of the 36th annual acm symposium on user interface software and technology*, pages 1–22, 2023\. 

J. S. Park, C. Q. Zou, A. Shaw, B. M. Hill, C. Cai, M. R. Morris, R. Willer, P. Liang, and M. S. Bernstein. Generative agent simulations of 1,000 people. *arXiv preprint arXiv:2411.10109*, 2024\. 

A. R. Poteete, M. A. Janssen, and E. Ostrom. *Working together: collective action, the commons, and multiple methods in practice*. Princeton University Press, 2010\. 

T. Raffaillac and S. Huot. Polyphony: Programming interfaces and interactions with the entity component-system model. *Proceedings of the ACM on Human-Computer Interaction*, 3(EICS):1–22, 2019\. 

K. Salen and E. Zimmerman. *Rules of Play: Game Design Fundamentals*. MIT Press, Cambridge, MA, 2003\. 

C. Schill, J. M. Anderies, T. Lindahl, C. Folke, S. Polasky, J. C. Cárdenas, A.-S. Crépin, M. A. Janssen, J. Norberg, and M. Schlüter. A more dynamic understanding of human behaviour for the anthro pocene. *Nature Sustainability*, 2(12):1075–1082, 2019\. 

12  
Multi-Actor Generative Artificial Intelligence as a Game Engine 

Y. Shao, V. Samuel, Y. Jiang, J. Yang, and D. Yang. Collaborative gym: A framework for enabling and evaluating human-agent collaboration. *arXiv preprint arXiv:2412.15701*, 2024\. 

D. Silver and R. S. Sutton. Welcome to the era of experience. *Google AI*, 1, 2025\. 

C. Smith, M. Abdulhai, M. Diaz, M. Tesic, R. Trivedi, A. Vezhnevets, L. Hammond, J. Clifton, M. Chang, E. A. Duéñez-Guzmán, J. P. Agapiou, J. Matyas, D. Karmon, and J. Z. Leibo. Evaluating generalization capabilities of LLM-based agents in mixed-motive scenarios using concordia. *arxiv*, 2025\. 

P. Sunehag and J. Z. Leibo. Simulation streams: A programming paradigm for controlling large language models and building complex systems with generative ai. *arXiv preprint arXiv:2501.18668*, 2025\. 

Unity Technologies. Unity 3D. URL https://unity.com/. 

A. S. Vezhnevets, J. P. Agapiou, A. Aharon, R. Ziv, J. Matyas, E. A. Duéñez-Guzmán, W. A. Cunningham, S. Osindero, D. Karmon, and J. Z. Leibo. Generative agent-based modeling with actions grounded in physical, social, or digital space using concordia. *arXiv preprint arXiv:2312.03664*, 2023\. 

W. Wu, H. Wu, L. Jiang, X. Liu, J. Hong, H. Zhao, and M. Zhang. From role-play to drama-interaction: An LLM solution. *arXiv preprint arXiv:2405.14231*, 2024\. 

Y. Xu, T. Chakraborty, S. Sharma, L. Nunes, E. Kıcıman, S. Lu, and R. Chandra. Direct reasoning optimization: Llms can reward and refine their own reasoning for open-ended tasks. *arXiv preprint arXiv:2506.13351*, 2025\. 

Y. Yang, H. Chai, Y. Song, S. Qi, M. Wen, N. Li, J. Liao, H. Hu, J. Lin, G. Chang, et al. A survey of ai agent protocols. *arXiv preprint arXiv:2504.16736*, 2025\. 

L. Yu, W. Jiang, H. Shi, J. Yu, Z. Liu, Y. Zhang, J. T. Kwok, Z. Li, A. Weller, and W. Liu. Metamath: Boot strap your own mathematical questions for large language models. *arXiv preprint arXiv:2309.12284*, 2023\. 

E. Zelikman, Y. Wu, J. Mu, and N. Goodman. Star: Bootstrapping reasoning with reasoning. *Advances in Neural Information Processing Systems*, 35:15476–15488, 2022\. 

Y. Zeng, Y. Wu, X. Zhang, H. Wang, and Q. Wu. Autodefense: Multi-agent llm defense against jailbreak attacks. *arXiv preprint arXiv:2403.04783*, 2024\. 

H. Zhang, W. Du, J. Shan, Q. Zhou, Y. Du, J. B. Tenenbaum, T. Shu, and C. Gan. Building cooperative embodied agents modularly with large language models. *arXiv preprint arXiv:2307.02485*, 2023\. 

X. Zhou, H. Zhu, L. Mathur, R. Zhang, H. Yu, Z. Qi, L.-P. Morency, Y. Bisk, D. Fried, G. Neubig, et al. Sotopia: Interactive evaluation for social intelligence in language agents. *arXiv preprint arXiv:2310.11667*, 2023\. 

13

[image1]: <data:image/png;base64,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>